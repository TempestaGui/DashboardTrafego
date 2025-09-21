const ctx = document.getElementById('trafegoChart').getContext('2d');
const drillCtx = document.getElementById('drillChart').getContext('2d');

let trafegoChart, drillChart;

// Criar gráfico principal (barras empilhadas)
trafegoChart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: [],
        datasets: [
            {
                label: 'In (bytes)',
                data: [],
                stack: 'Stack 0',
                backgroundColor: 'rgba(54, 162, 235, 0.6)',
                borderColor: 'rgb(54, 162, 235)',
                borderWidth: 1
            },
            {
                label: 'Out (bytes)',
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
        scales: {
            x: { stacked: true, title: { display: true, text: 'Clientes (IP)' } },
            y: { stacked: true, title: { display: true, text: 'Bytes' } }
        },
        onClick: (evt, activeEls) => {
            if (activeEls.length > 0) {
                const idx = activeEls[0].index;
                const clientIp = trafegoChart.data.labels[idx];
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

        trafegoChart.data.labels = top.map(x => x.client);
        trafegoChart.data.datasets[0].data = top.map(x => x.in);
        trafegoChart.data.datasets[1].data = top.map(x => x.out);

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

        const labels = Object.keys(json.protocols);
        const values = Object.values(json.protocols);

        if (drillChart) drillChart.destroy();

        drillChart = new Chart(drillCtx, {
            type: 'pie',
            data: {
                labels,
                datasets: [{
                    data: values,
                    backgroundColor: [
                        'rgba(32, 70, 95, 0.6)',
                        'rgba(255, 99, 132, 0.6)',
                        'rgba(255, 206, 86, 0.6)',
                        'rgba(75, 192, 192, 0.6)',
                        'rgba(153, 102, 255, 0.6)'
                    ]
                }]
            },
            options: {
                responsive: true
            }
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
