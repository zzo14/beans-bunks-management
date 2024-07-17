document.addEventListener("DOMContentLoaded", function() {
    createProductSalesCharts(productSalesReportData, popularProductReportData);
});

const salesData = {
    labels: [],
    datasets: [
        {
            label: 'Revenue',
            type: 'bar',
            data: [],
            backgroundColor: '#6F4E37', // coffee brown
            yAxisID: 'y',
        },
    ]
}

const salesDistributionData = {
    labels: [],
    datasets: [{
        data: [],
        backgroundColor: [
            '#C19A6B', // light brown
            '#6F4E37', // brown
            '#F4E1C1', // light tan
            '#8B4513',  // bronze
            '#D2B48C',  // tan
            '#CD853F',  // peru
        ]
    }]
};

const popularProductsData = {
    labels: [],
    datasets: [{
        label: 'Sales Quantity',
        data: [],
        backgroundColor: '#6F4E37', // coffee brown
    }]
};

let productSalesChart = null;
let salesDistributionPieChart = null;
let popularProductsChart = null;

function resetProductSalesData() {
    salesData.labels = [];
    salesData.datasets[0].data = [];
    salesDistributionData.labels = [];
    salesDistributionData.datasets[0].data = [];
    popularProductsData.labels = [];
    popularProductsData.datasets[0].data = [];
}

function processProductSalesData(productSalesData, popularProductData) {
    resetProductSalesData();

    const categoryData = {};
    const includeGST = document.getElementById('productSalesIncludeGST').checked;
    const gstFactor = includeGST ? 1 : 0.85;

    productSalesData.forEach(item => {
        const productName = item[1];
        const salesQuantity = parseInt(item[2]);
        const totalRevenue = parseFloat(item[3]) * gstFactor;
        const category = item[4];

        salesData.labels.push(productName);
        salesData.datasets[0].data.push(totalRevenue);

        if (!categoryData[category]) {
            categoryData[category] = 0;
        }
        categoryData[category] += totalRevenue;
    });

    for (const category in categoryData) {
        salesDistributionData.labels.push(category);
        salesDistributionData.datasets[0].data.push(categoryData[category]);
    }

    popularProductData.forEach(item => {
        const productName = item[1];
        const salesQuantity = parseInt(item[2]);

        popularProductsData.labels.push(productName);
        popularProductsData.datasets[0].data.push(salesQuantity);
    });
}

function createProductSalesCharts(productSalesData, popularProductData) {
    if (!productSalesData || productSalesData.length === 0) {
        console.error("Product sales data is not loaded");
        return;
    } else if (!popularProductData || popularProductData.length === 0) {
        console.error("Popular product data is not loaded");
        return;
    }

    if (productSalesChart) {
        productSalesChart.destroy();
    }
    if (salesDistributionPieChart) {
        salesDistributionPieChart.destroy();
    }
    if (popularProductsChart) {
        popularProductsChart.destroy();
    }

    processProductSalesData(productSalesData, popularProductData);

    const productSalesCanvas = document.getElementById('productSalesChart').getContext('2d');
    productSalesChart = new Chart(productSalesCanvas, {
        type: 'bar',
        data: salesData,
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    position: 'left',
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

            },
            plugins: {
                tooltip: {
                    displayColors: false,
                    callbacks: {
                        label: function(context) {
                            let label = 'Total Revenue: $' + context.raw.toFixed(2);
                            return label;
                        },
                        afterLabel: function(context) {
                            return 'Sales Quantity: ' + productSalesData[context.dataIndex][2];
                        }
                    }
                }
            },
        }
    });

    const salesDistributionCanvas = document.getElementById('salesDistributionPieChart').getContext('2d');
    salesDistributionPieChart = new Chart(salesDistributionCanvas, {
        type: 'pie',
        data: salesDistributionData,
        options: {
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = '';
                            label = 'Total Revenue: $' + context.raw.toFixed(2);
                            return label;
                        },
                    }
                }
            },
        }
    });

    const popularProductsCanvas = document.getElementById('popularProductsChart').getContext('2d');
    popularProductsChart = new Chart(popularProductsCanvas, {
        type: 'bar',
        data: popularProductsData,
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Sales Quantity',
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
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = '';
                            label = 'Sales Quantity: ' + context.raw;
                            return label;
                        },
                    }
                }
            },
        }
    });
}

function updateProductSalesCharts() {
    createProductSalesCharts(productSalesReportData, popularProductReportData);
}