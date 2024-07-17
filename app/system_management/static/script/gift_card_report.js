document.addEventListener('DOMContentLoaded', function() {
    createGiftCardCharts(giftCardSalesData, giftCardUsageData);
});

const giftCardSalesDataConfig = {
    labels: [],
    datasets: [{
        label: 'Revenue',
        data: [],
        backgroundColor: '#C19A6B', // light brown
        borderColor: '#8B4513', // bronze
        fill: false,
        maxBarThickness: 75,
    }]
};

const giftCardUsageDataConfig = {
    labels: [],
    datasets: [{
        data: [],
        backgroundColor: [
            '#6F4E37', // coffee brown
            '#D2B48C', // tan
            '#8B4513', // bronze
        ]
    }]
};

let giftCardSalesChart = null;
let giftCardUsageChart = null;

function resetGiftCardData() {
    giftCardSalesDataConfig.labels = [];
    giftCardSalesDataConfig.datasets[0].data = [];
    giftCardUsageDataConfig.labels = [];
    giftCardUsageDataConfig.datasets[0].data = [];
}

function processGiftCardData(salesReportData, usageReportData) {
    resetGiftCardData();

    salesReportData.forEach(item => {
        const typeDescription = item[2];
        const salesCount = parseInt(item[3]);

        giftCardSalesDataConfig.labels.push(typeDescription);
        giftCardSalesDataConfig.datasets[0].data.push(salesCount);
    });

    usageReportData.forEach(item => {
        const amount = item[0];
        const totalCount = parseInt(item[1]);

        giftCardUsageDataConfig.labels.push(`$${amount}`);
        giftCardUsageDataConfig.datasets[0].data.push(totalCount);
    });
}

function createGiftCardCharts(salesReportData, usageReportData) {
    processGiftCardData(salesReportData, usageReportData);

    const salesCtx = document.getElementById('giftCardSalesChart').getContext('2d');
    giftCardSalesChart = new Chart(salesCtx, {
        type: 'bar',
        data: giftCardSalesDataConfig,
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Revenue',
                        font:{
                            weight: 'bold'
                        }
                    },
                    ticks: {
                        callback: function(value) {
                            return '$' + value;
                        }
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Gift Card Type',
                        font:{
                            weight: 'bold'
                        }
                    }
                }
            },
            plugins: {
                displayColors: false,
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            label += '$' + context.raw;
                            return label;
                        }
                    }
                }
            }
        }
    });

    const usageCtx = document.getElementById('giftCardUsageChart').getContext('2d');
    giftCardUsageChart = new Chart(usageCtx, {
        type: 'pie',
        data: giftCardUsageDataConfig,
        options: {
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = giftCardUsageDataConfig.labels[context.dataIndex] || '';
                            if (label) {
                                label = 'Sales Quantity: ';
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
