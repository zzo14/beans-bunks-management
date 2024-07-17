document.addEventListener("DOMContentLoaded", function() {
    createProductReviewChart(topReviewData);
});

const reviewData = {
    labels: [],
    datasets: [
        {
            label: 'Average Rating',
            type: 'bar',
            data: [],
            backgroundColor: '#6F4E37', // coffee brown
            yAxisID: 'y',
        },
    ]
};

let productReviewChart = null;

function resetReviewData() {
    reviewData.labels = [];
    reviewData.datasets[0].data = [];
}

function processReviewData(topReviewData) {
    resetReviewData();

    topReviewData.forEach(item => {
        const productName = item[1];
        const averageRating = parseFloat(item[3]);
        const totalRatings = parseInt(item[4]);

        reviewData.labels.push(productName);
        reviewData.datasets[0].data.push(averageRating);
    });
}

function createProductReviewChart(topReviewData) {
    if (!topReviewData || topReviewData.length === 0) {
        console.error("Top review data is not loaded");
        return;
    }

    if (productReviewChart) {
        productReviewChart.destroy();
    }

    processReviewData(topReviewData);

    const reviewCanvas = document.getElementById('productReviewChart').getContext('2d');
    productReviewChart = new Chart(reviewCanvas, {
        type: 'bar',
        data: reviewData,
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Average Rating',
                        font:{
                            weight: 'bold'
                        }
                    },
                    ticks: {
                        max: 5,
                        min: 0
                    }
                }
            },
            plugins: {
                tooltip: {
                    displayColors: false,
                    callbacks: {
                        label: function(context) {
                            let label = 'Average Rating: ' + context.raw.toFixed(1);
                            return label;
                        },
                        afterLabel: function(context) {
                            let index = context.dataIndex;
                            let totalRatings = topReviewData[index][4];
                            return 'Total Ratings: ' + totalRatings;
                        }
                    }
                }
            },
        }
    });
}

function updateProductReviewChart() {
    createProductReviewChart(topReviewData);
}
