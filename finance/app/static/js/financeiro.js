// Gráfico de Linha (Vendas por Dia)
    const ctxVendas = document.getElementById('chartVendas').getContext('2d');
    new Chart(ctxVendas, {
        type: 'line',
        data: {
            labels: {{ charts.dias|safe }},
            datasets: [{
                label: 'Vendas (R$)',
                data: {{ charts.vendas_dia|safe }},
                borderColor: '#4e73df',
                backgroundColor: 'rgba(78, 115, 223, 0.05)',
                tension: 0.3,
                fill: true
            }]
        },
        options: { scales: { y: { beginAtZero: true } } }
    });

    // Gráfico de Rosca (Custos)
    const ctxCustos = document.getElementById('chartCustos').getContext('2d');
    new Chart(ctxCustos, {
        type: 'doughnut',
        data: {
            labels: {{ charts.custos_labels|safe }},
            datasets: [{
                data: {{ charts.custos_values|safe }},
                backgroundColor: ['#4e73df', '#1cc88a', '#36b9cc'],
            }]
        },
        options: { cutout: '70%' }
    });