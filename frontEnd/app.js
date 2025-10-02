// Referências aos elementos canvas - obtém contextos 2D para renderização dos gráficos
const ctx = document.getElementById('trafegoChart')?.getContext('2d');
const drillCtx = document.getElementById('drillChart')?.getContext('2d');

// Verificação de segurança - garante que os canvas existem no DOM
if (!ctx || !drillCtx) {
    console.error("Erro: elementos canvas não encontrados!");
}

// Variáveis globais para armazenar instâncias dos gráficos Chart.js
let trafegoChart, drillChart;

// Cores associadas a protocolos
const protocolColors = {
    TCP: 'rgba(54, 162, 235, 0.7)',
    UDP: 'rgba(255, 206, 86, 0.7)',
    ICMP: 'rgba(255, 99, 132, 0.7)',
    OTHER: 'rgba(153, 102, 255, 0.7)'
};

// Descrições detalhadas de cada protocolo
const protocolDescriptions = {
    TCP: "Transmission Control Protocol – garante entrega confiável e ordenada.",
    UDP: "User Datagram Protocol – mais rápido, sem confirmação de entrega.",
    ICMP: "Internet Control Message Protocol – usado para mensagens de controle (ex: ping).",
    HTTP: "HyperText Transfer Protocol – usado para páginas web.",
    HTTPS: "HTTP Secure – versão criptografada do HTTP.",
    DNS: "Domain Name System – resolve nomes de domínio para endereços IP.",
    OTHER: "Outros protocolos menos comuns.",
    ["Sem tráfego"]: "Nenhum tráfego registrado nesta janela de tempo."
};

// Dica abaixo do gráfico principal
const legendGrafico = document.getElementById("legend");
if (legendGrafico) {
    legendGrafico.innerHTML = "";
    const desc = document.createElement("p");
    desc.textContent = " 💡 Dica: Aperte em uma das colunas para visualizar o DrillDown";
    legendGrafico.appendChild(desc);
} else {
    console.warn("Elemento 'legend' não encontrado");
}

/**
 * Converte valores em bytes para unidades legíveis (KB, MB, GB, TB)
 * 
 * @param {number} bytes - Valor em bytes para ser convertido
 * @returns {string} Valor formatado com unidade apropriada (ex: "1.5 MB")
 * 
 * Funcionalidade:
 * - Valida se o input é um número válido
 * - Para valores < 1024, retorna em bytes
 * - Calcula automaticamente a unidade apropriada (KB/MB/GB/TB)
 * - Retorna valor formatado com 1 casa decimal
 * - Em caso de erro, retorna "0 B" como fallback
 */
function formatBytes(bytes) {
    try {
        if (typeof bytes !== "number" || isNaN(bytes)) return "0 B";
        if (bytes < 1024) return bytes + ' B';
        let k = 1024;
        let sizes = ['KB', 'MB', 'GB', 'TB'];
        let i = Math.floor(Math.log(bytes) / Math.log(k));
        return (bytes / Math.pow(k, i)).toFixed(1) + ' ' + sizes[i - 1];
    } catch (err) {
        console.error("Erro formatando bytes:", err);
        return "0 B";
    }
}

/**
 * Inicializa o gráfico principal de tráfego usando Chart.js
 * 
 * Funcionalidade:
 * - Cria gráfico de barras empilhadas para mostrar tráfego de entrada/saída
 * - Configura tooltips personalizados com formatação de bytes
 * - Implementa interatividade (clique nas barras abre drilldown)
 * - Define escalas e responsividade
 * - Armazena metadados (IP e hostname) para cada cliente
 * 
 * Estrutura dos dados:
 * - Labels: nomes dos clientes (hostname ou IP)
 * - Dataset 1: Bytes de entrada (azul)
 * - Dataset 2: Bytes de saída (laranja)
 * - Meta: informações adicionais (IP, hostname) para tooltips e drilldown
 */
function criarGraficoPrincipal() {
    try {
        trafegoChart = new Chart(ctx, {
            type: 'bar',
            data: { 
                labels: [], 
                datasets: [
                    { label: 'Entrada (bytes)', data: [], stack: 'Stack 0', backgroundColor: 'rgba(54, 162, 235, 0.6)', borderColor: 'rgb(54, 162, 235)', borderWidth: 1 },
                    { label: 'Saída (bytes)', data: [], stack: 'Stack 0', backgroundColor: 'rgba(255, 159, 64, 0.6)', borderColor: 'rgb(255, 159, 64)', borderWidth: 1 }
                ], 
                meta: [] 
            },
            options: {
                responsive: true,
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `${context.dataset.label}: ${formatBytes(context.raw)}`;
                            },
                            afterBody: function(context) {
                                let idx = context[0]?.dataIndex;
                                let meta = trafegoChart?.data?.meta[idx] || {};
                                return [`IP: ${meta.ip || 'N/A'}`, `Host: ${meta.hostname || 'N/A'}`];
                            }
                        }
                    }
                },
                scales: {
                    x: { stacked: true, title: { display: true, text: 'Clientes' } },
                    y: { stacked: true, title: { display: true, text: 'Bytes' }, beginAtZero: true }
                },
                onClick: async (evt, activeEls) => {
                    try {
                        if (activeEls.length > 0) {
                            const idx = activeEls[0]?.index;
                            const clientIp = trafegoChart?.data?.meta[idx]?.ip;
                            if (clientIp) {
                                await abrirDrilldown(clientIp);
                            } else {
                                alert("IP não identificado na barra selecionada.");
                            }
                        }
                    } catch (err) {
                        console.error("Erro ao abrir drilldown:", err);
                    }
                }
            }
        });
    } catch (err) {
        console.error("Erro criando gráfico principal:", err);
    }
}

/**
 * Atualiza os dados do gráfico principal consultando a API do backend
 * 
 * Funcionalidade:
 * - Faz requisição HTTP para endpoint /trafego/current
 * - Processa resposta JSON e extrai dados de tráfego
 * - Seleciona top 10 clientes com maior tráfego
 * - Atualiza labels, datasets e metadados do gráfico
 * - Trata erros de rede e API
 * - Garante que o gráfico existe antes de atualizar
 * 
 * Fluxo de dados:
 * 1. Fetch da API -> JSON com dados de clientes
 * 2. Slice dos top 10 -> Array limitado
 * 3. Map para labels -> Hostnames ou IPs
 * 4. Map para datasets -> Bytes in/out separados
 * 5. Update do Chart.js -> Renderização visual
 */
async function atualizarGrafico() {
    try {
        const res = await fetch('http://127.0.0.1:8001/trafego/current');
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const json = await res.json();
        const data = json.data || [];

        const top = data.slice(0, 10);
        if (!trafegoChart) criarGraficoPrincipal();

        trafegoChart.data.labels = top.map(x => x.hostname || x.client);
        trafegoChart.data.datasets[0].data = top.map(x => x.in || 0);
        trafegoChart.data.datasets[1].data = top.map(x => x.out || 0);
        trafegoChart.data.meta = top.map(x => ({ ip: x.client, hostname: x.hostname })) || [];

        trafegoChart.update();
    } catch (err) {
        console.error("Erro ao atualizar gráfico:", err);
    }
}
// Configura atualização automática do gráfico a cada 5 segundos
setInterval(atualizarGrafico, 5000);

/**
 * Abre a visualização detalhada (drilldown) dos protocolos de um cliente específico
 * 
 * @param {string} clientIp - Endereço IP do cliente para análise detalhada
 * 
 * Funcionalidade:
 * - Consulta API /trafego/drilldown/{clientIp} para dados específicos
 * - Exibe seção drilldown (remove classe 'hidden')
 * - Cria gráfico de pizza mostrando distribuição de protocolos
 * - Gera legenda explicativa para cada protocolo
 * - Trata caso especial de "sem tráfego"
 * - Destrói gráfico anterior se existir (evita sobreposição)
 * 
 * Estados tratados:
 * - Cliente com tráfego: gráfico colorido com protocolos reais
 * - Cliente sem tráfego: gráfico cinza com mensagem informativa
 * - Erro de API: alerta ao usuário e log de erro
 */
async function abrirDrilldown(clientIp) {
    try {
        const res = await fetch(`http://127.0.0.1:8001/trafego/drilldown/${clientIp}`);
        if (!res.ok) throw new Error(`IP ${clientIp} não encontrado na janela atual`);
        const json = await res.json();

        const drillSection = document.getElementById("drilldown");
        if (!drillSection) throw new Error("Elemento drilldown não encontrado");

        document.getElementById("drill-client").innerText = clientIp;
        drillSection.classList.remove("hidden");

        let labels = json.protocols ? Object.keys(json.protocols) : [];
        let values = json.protocols ? Object.values(json.protocols) : [];
        let bgColors = [];

        if (labels.length === 0) {
            labels = ["Sem tráfego"];
            values = [1];
            document.getElementById("drill-client").innerText = `– Nenhum tráfego de ${clientIp} registrado nesta janela`;
            bgColors = ['rgba(200,200,200,0.7)'];
        }

        if (drillChart) drillChart.destroy();

        drillChart = new Chart(drillCtx, {
            type: 'pie',
            data: { 
                labels, 
                datasets:[{
                    data: values,
                    backgroundColor: bgColors.length ? bgColors : labels.map(l => protocolColors[l] || 'rgba(200,200,200,0.6)'),
                    borderColor: 'rgba(0,0,0,0.3)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context){
                                if(values[context.dataIndex] < 0.02) return null;
                                return `${context.label}: ${formatBytes(context.raw)}`;
                            }
                        }
                    }
                }
            }
        });

        // Legenda textual do drilldown
        const legend = document.getElementById("protocol-legend");
        if (legend) {
            legend.innerHTML = "";
            const legendKeys = labels.length === 1 && labels[0] === "Sem tráfego" ? ["Sem tráfego"] : Object.keys(json.protocols || {});
            legendKeys.forEach(proto => {
                const desc = protocolDescriptions[proto] || "Sem descrição disponível.";
                const item = document.createElement("p");
                item.innerHTML = `<strong>${proto}:</strong> ${desc}`;
                legend.appendChild(item);
            });
        }

    } catch (err) {
        console.error("Erro drilldown:", err);
        alert(`Erro ao obter dados de ${clientIp}. Veja console para detalhes.`);
    }
}

/**
 * Fecha a visualização de drilldown e limpa recursos associados
 * 
 * Funcionalidade:
 * - Oculta seção drilldown (adiciona classe 'hidden')
 * - Destrói instância do gráfico Chart.js para liberar memória
 * - Define variável drillChart como null
 * - Trata erros durante o processo de fechamento
 * 
 * Limpeza de recursos:
 * - Remove elementos visuais do DOM
 * - Libera memória ocupada pelo gráfico Chart.js
 * - Previne vazamentos de memória em uso prolongado
 * - Prepara interface para próximo drilldown
 */
function fecharDrilldown() {
    try {
        const drillSection = document.getElementById("drilldown");
        if (!drillSection) return;
        drillSection.classList.add("hidden");
        if (drillChart) {
            drillChart.destroy();
            drillChart = null;
        }
    } catch (err) {
        console.error("Erro fechando drilldown:", err);
    }
}

// Controle do menu de integrantes
try {
    const menu = document.getElementById("menu");
    const trigger = document.getElementById("menu-trigger");
    if (menu && trigger) {
        trigger.addEventListener("click", () => {
            const aberto = menu.getAttribute("data-aberto") === "true";
            menu.setAttribute("data-aberto", !aberto);
        });
    } else {
        console.warn("Menu ou trigger não encontrados");
    }
} catch (err) {
    console.error("Erro configurando menu:", err);
}

// Inicialização do dashboard ao carregar a página
criarGraficoPrincipal();
atualizarGrafico();