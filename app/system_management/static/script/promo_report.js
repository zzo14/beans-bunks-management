document.addEventListener('DOMContentLoaded', function() {
    createPromotionChart(promoEffectivenessData);
});

const promotionData = {
    labels: [],
    datasets: [{
        label: 'Usage Count',
        data: [],
        backgroundColor: [
            '#C19A6B', // light brown
        ],
        maxBarThickness: 75,
    }]
};

let promotionChart = null;

function resetPromotionData() {
    promotionData.labels = [];
    promotionData.datasets[0].data = [];
}

function processPromotionData(promoReportData) {
    resetPromotionData();

    promoReportData.forEach(item => {
        const promotionCode = item[1];
        const usageCount = item[2];

        promotionData.labels.push(promotionCode);
        promotionData.datasets[0].data.push(usageCount);
    });
}

function createPromotionChart(promoReportData) {
    processPromotionData(promoReportData);

    const ctx = document.getElementById('promotionEffectivenessChart').getContext('2d');
    promotionEffectivenessChart = new Chart(ctx, {
        type: 'bar',
        data: promotionData,
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Usage Count',
                        font:{
                            weight: 'bold'
                        }
                    },
                    ticks: {
                        callback: function(value) {
                            if (value % 1 === 0) {
                                return value;
                            }
                        }
                    },
                },
                x: {
                    title: {
                        display: true,
                        text: 'Promotion Code',
                        font:{
                            weight: 'bold'
                        }
                    },
                }
            },
            plugin: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            label += context.raw;
                            return label;
                        }
                    }
                }
            }
        }
    });
}