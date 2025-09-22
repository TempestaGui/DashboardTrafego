const ctx = document.getElementById('trafegoChart').getContext('2d');
const drillCtx = document.getElementById('drillChart').getContext('2d');

let trafegoChart, drillChart;
//descricao protocolo
// Descrições dos protocolos
const protocolDescriptions = {
    TCP: "Transmission Control Protocol – garante entrega confiável e ordenada.",
    UDP: "User Datagram Protocol – mais rápido, sem confirmação de entrega.",
    ICMP: "Internet Control Message Protocol – usado para mensagens de controle (ex: ping).",
    HTTP: "HyperText Transfer Protocol – usado para páginas web.",
    HTTPS: "HTTP Secure – versão criptografada do HTTP.",
    DNS: "Domain Name System – resolve nomes de domínio para endereços IP.",
    OTHER: "Outros protocolos menos comuns."
};


// Paleta fixa de cores para protocolos
const protocolColors = {
    TCP: 'rgba(54, 162, 235, 0.7)',
    UDP: 'rgba(255, 206, 86, 0.7)',
    ICMP: 'rgba(255, 99, 132, 0.7)',
    OTHER: 'rgba(153, 102, 255, 0.7)'
};

// Helper para formatar bytes
function formatBytes(bytes) {
    if (bytes < 1024) return bytes + ' B';
    let k = 1024;
    let sizes = ['KB', 'MB', 'GB', 'TB'];
    let i = Math.floor(Math.log(bytes) / Math.log(k));
    return (bytes / Math.pow(k, i)).toFixed(1) + ' ' + sizes[i - 1];
}

// Criar gráfico principal (barras empilhadas)
trafegoChart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: [],
        datasets: [
            {
                label: 'Entrada (bytes)',
                data: [],
                stack: 'Stack 0',
                backgroundColor: 'rgba(54, 162, 235, 0.6)',
                borderColor: 'rgb(54, 162, 235)',
                borderWidth: 1
            },
            {
                label: 'Saída (bytes)',
                data: [],
                stack: 'Stack 0',
                backgroundColor: 'rgba(255, 159, 64, 0.6)',
                borderColor: 'rgb(255, 159, 64)',
                borderWidth: 1
            }
        ]
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
                        let idx = context[0].dataIndex;
                        let ip = trafegoChart.data.meta[idx].ip;
                        let hostname = trafegoChart.data.labels[idx];
                        return [`IP: ${ip}`, `Host: ${hostname}`];
                    }
                }
            }
        },
        scales: {
            x: { stacked: true, title: { display: true, text: 'Clientes' } },
            y: { stacked: true, title: { display: true, text: 'Bytes' } }
        },
        onClick: (evt, activeEls) => {
            if (activeEls.length > 0) {
                const idx = activeEls[0].index;
                const clientIp = trafegoChart.data.meta[idx].ip;
                abrirDrilldown(clientIp);
            }
        }
    }
});

// Atualiza gráfico principal a cada 2s
async function atualizarGrafico() {
    try {
        const res = await fetch('http://127.0.0.1:8001/trafego/current');
        const json = await res.json();
        const data = json.data || [];

        const top = data.slice(0, 10); // mostra os 10 maiores clientes

        trafegoChart.data.labels = top.map(x => x.hostname || x.client);
        trafegoChart.data.datasets[0].data = top.map(x => x.in);
        trafegoChart.data.datasets[1].data = top.map(x => x.out);

        // armazenar metadados (hostname/ip separados)
        trafegoChart.data.meta = top.map(x => ({ ip: x.client, hostname: x.hostname }));

        trafegoChart.update();
    } catch (err) {
        console.error("Erro ao buscar dados:", err);
    }
}
setInterval(atualizarGrafico, 2000);

// Drilldown (abre gráfico de protocolos)
async function abrirDrilldown(clientIp) {
    try {
        const res = await fetch(`http://127.0.0.1:8001/trafego/drilldown/${clientIp}`);
        const json = await res.json();

        document.getElementById("drill-client").innerText = clientIp;
        document.getElementById("drilldown").classList.remove("hidden");

        let labels = Object.keys(json.protocols);
        let values = Object.values(json.protocols);

        // Simula pequenas fatias extras se houver apenas 1 protocolo
        if (labels.length === 1) {
            // Adiciona protocolos “fantasmas” para efeito visual
            const dummyProtos = Object.keys(protocolColors).filter(p => p !== labels[0]);
            labels = labels.concat(dummyProtos);
            values = values.concat(dummyProtos.map(() => 0.01)); // valor mínimo para renderizar a cor
        }

        if (drillChart) drillChart.destroy();

        drillChart = new Chart(drillCtx, {
            type: 'pie',
            data: {
                labels,
                datasets: [{
                    data: values,
                    backgroundColor: labels.map(l => protocolColors[l] || 'rgba(200,200,200,0.6)'),
                    borderColor: 'rgba(0,0,0,0.3)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                // Não mostrar os "dummy" no tooltip
                                if (values[context.dataIndex] < 0.02) return null;
                                return `${context.label}: ${formatBytes(context.raw)}`;
                            }
                        }
                    }
                }
            }
        });

        // Monta legenda de significados
        const legend = document.getElementById("protocol-legend");
        legend.innerHTML = ""; // limpa antes
        Object.keys(json.protocols).forEach(proto => {
            const desc = protocolDescriptions[proto] || "Sem descrição disponível.";
            const item = document.createElement("p");
            item.innerHTML = `<strong>${proto}:</strong> ${desc}`;
            legend.appendChild(item);
        });

    } catch (err) {
        console.error("Erro drilldown:", err);
    }
}


// Fechar drilldown
function fecharDrilldown() {
    document.getElementById("drilldown").classList.add("hidden");
    if (drillChart) {
        drillChart.destroy();
        drillChart = null;
    }
}
