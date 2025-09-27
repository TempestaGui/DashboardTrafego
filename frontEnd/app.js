// Canvas e contexto
const ctx = document.getElementById('trafegoChart').getContext('2d');
const drillCtx = document.getElementById('drillChart').getContext('2d');

let trafegoChart, drillChart;

// Paleta de cores por protocolo
const protocolColors = {
    TCP: 'rgba(54, 162, 235, 0.7)',
    UDP: 'rgba(255, 206, 86, 0.7)',
    ICMP: 'rgba(255, 99, 132, 0.7)',
    OTHER: 'rgba(153, 102, 255, 0.7)'
};

// Descrição dos protocolos
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

// Monta legenda do gráfico principal
const legendGrafico = document.getElementById("legend");
legendGrafico.innerHTML = "";
const desc = document.createElement("p");
desc.textContent = " 💡 Aperte em uma das colunas para visualizar o DrillDown";
legendGrafico.appendChild(desc);

// Helper para formatar bytes
function formatBytes(bytes) {
    if (bytes < 1024) return bytes + ' B';
    let k = 1024;
    let sizes = ['KB', 'MB', 'GB', 'TB'];
    let i = Math.floor(Math.log(bytes) / Math.log(k));
    return (bytes / Math.pow(k, i)).toFixed(1) + ' ' + sizes[i - 1];
}

// Cria gráfico principal (barras empilhadas)
trafegoChart = new Chart(ctx, {
    type: 'bar',
    data: { labels: [], datasets: [
        { label: 'Entrada (bytes)', data: [], stack: 'Stack 0', backgroundColor: 'rgba(54, 162, 235, 0.6)', borderColor: 'rgb(54, 162, 235)', borderWidth: 1 },
        { label: 'Saída (bytes)', data: [], stack: 'Stack 0', backgroundColor: 'rgba(255, 159, 64, 0.6)', borderColor: 'rgb(255, 159, 64)', borderWidth: 1 }
    ], meta: [] },
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
                        let meta = trafegoChart.data.meta[idx] || {};
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
            if (activeEls.length > 0) {
                const idx = activeEls[0].index;
                const clientIp = trafegoChart.data.meta[idx]?.ip;
                if(clientIp) {
                    try {
                        await abrirDrilldown(clientIp);
                    } catch(err) {
                        alert("Nenhum tráfego registrado para este IP na janela atual.");
                    }
                }
            }
        }
    }
});

// Atualiza gráfico principal a cada 5s
async function atualizarGrafico() {
    try {
        const res = await fetch('http://127.0.0.1:8001/trafego/current');
        const json = await res.json();
        const data = json.data || [];

        const top = data.slice(0, 10);

        trafegoChart.data.labels = top.map(x => x.hostname || x.client);
        trafegoChart.data.datasets[0].data = top.map(x => x.in);
        trafegoChart.data.datasets[1].data = top.map(x => x.out);
        trafegoChart.data.meta = top.map(x => ({ ip: x.client, hostname: x.hostname })) || [];

        trafegoChart.update();
    } catch (err) {
        console.error("Erro ao buscar dados:", err);
    }
}
setInterval(atualizarGrafico, 5000);

// Drilldown: gráficos de protocolo por cliente
async function abrirDrilldown(clientIp) {
    try {
        const res = await fetch(`http://127.0.0.1:8001/trafego/drilldown/${clientIp}`);
        if(!res.ok) throw new Error("IP não encontrado na janela atual");
        const json = await res.json();

        document.getElementById("drill-client").innerText = clientIp;
        document.getElementById("drilldown").classList.remove("hidden");

        let labels = json.protocols ? Object.keys(json.protocols) : [];
        let values = json.protocols ? Object.values(json.protocols) : [];
        let bgColors = [];

        if(labels.length === 0){
            labels = ["Sem tráfego"];
            values = [1];
                document.getElementById("drill-client").innerText = `– Nenhum tráfego de ${clientIp} registrado nesta janela`;
                bgColors = ['rgba(200,200,200,0.7)'];
        }
         

        if(drillChart) drillChart.destroy();

        drillChart = new Chart(drillCtx, {
            type: 'pie',
            data: { labels, datasets:[{
                data: values,
                backgroundColor: bgColors.length ? bgColors : labels.map(l => protocolColors[l] || 'rgba(200,200,200,0.6)'),
                borderColor: 'rgba(0,0,0,0.3)',
                borderWidth: 1
            }]},
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

        // Legenda do drilldown
        const legend = document.getElementById("protocol-legend");
        legend.innerHTML = "";
const legendKeys = labels.length === 1 && labels[0] === "Sem tráfego" ? ["Sem tráfego"] : Object.keys(json.protocols || {});
legendKeys.forEach(proto => {
    const desc = protocolDescriptions[proto] || "Sem descrição disponível.";
    const item = document.createElement("p");
    item.innerHTML = `<strong>${proto}:</strong> ${desc}`;
    legend.appendChild(item);
});


    } catch(err) {
        console.error("Erro drilldown:", err);
    }
}

// Fechar drilldown
function fecharDrilldown(){
    document.getElementById("drilldown").classList.add("hidden");
    if(drillChart){
        drillChart.destroy();
        drillChart = null;
    }
}
