// Dados de Contexto do Django
// O filtro 'unlocalize' é necessário aqui para remover a formatação regional
// e permitir que o JavaScript interprete o número corretamente.
const faturamentoBruto = parseFloat("{{ faturamento_bruto_mensal|unlocalize|default:0.00 }}");
const custoVariavelTotal = parseFloat("{{ custo_variavel_total_total|unlocalize|default:0.00 }}");
const custoFixoTotal = parseFloat("{{ custo_fixo_total|unlocalize|default:0.00 }}");
const lucroLiquido = parseFloat("{{ lucro_liquido|unlocalize|default:0.00 }}");

window.onload = function() {
    const ctx = document.getElementById('revenueCostChart').getContext('2d');

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Faturamento Bruto', 'Custo Variável Total', 'Custo Fixo Total', 'Lucro Líquido'],
            datasets: [{
                label: 'Valores Mensais (R$)',
                data: [faturamentoBruto, custoVariavelTotal, custoFixoTotal, lucroLiquido],
                backgroundColor: [
                    'rgba(79, 70, 229, 0.8)', // Indigo for Revenue
                    'rgba(245, 101, 101, 0.8)', // Red for Variable Cost
                    'rgba(249, 115, 22, 0.8)', // Orange for Fixed Cost
                    'rgba(16, 185, 129, 0.8)' // Green for Net Profit
                ],
                borderColor: [
                    'rgba(79, 70, 229, 1)',
                    'rgba(245, 101, 101, 1)',
                    'rgba(249, 115, 22, 1)',
                    'rgba(16, 185, 129, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Valor (R$)'
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed.y !== null) {
                                label += new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(context.parsed.y);
                            }
                            return label;
                        }
                    }
                }
            }
        }
    });
}