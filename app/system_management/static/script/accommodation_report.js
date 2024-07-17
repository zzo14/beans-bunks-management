document.addEventListener("DOMContentLoaded", function() {
    populateAccommodationYearSelector();
    updateAccommodationCharts();
});

const accommodationOccupancyData = {
    labels: [],
    datasets: [
        {
            label: 'Revenue',
            type: 'line',
            data: [],
            borderColor: '#D2B48C', // tan
            backgroundColor: 'rgba(210, 180, 140, 0.2)', // light tan with transparency
            fill: true,
            yAxisID: 'y',
        },
        {
            label: 'Booking Count',
            type: 'bar',
            data: [],
            backgroundColor: '#6F4E37', // coffee brown
            yAxisID: 'y1',
            maxBarThickness: 75,
        }
    ]
};

const accommodationRoomTypeData = {
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
        ],
    }],
    revenueData: [],
};
let occupancyBarChart = null;
let roomTypePieChart = null;

function resetAccommodationData() {
    accommodationOccupancyData.labels = [];
    accommodationOccupancyData.datasets[0].data = [];
    accommodationOccupancyData.datasets[1].data = [];
    accommodationRoomTypeData.labels = [];
    accommodationRoomTypeData.datasets[0].data = [];
    accommodationRoomTypeData.revenueData = [];
}

function processAccommodationData(monthlyData, roomTypeData) {
    resetAccommodationData();

    const includeGST = document.getElementById('accommodationIncludeGST').checked;
    const gstFactor = includeGST ? 1 : 0.85;

    monthlyData.forEach(item => {
        const year = item[0];
        const month = item[1];
        const bookingCount = item[2];
        const totalRevenue = parseFloat(item[3]) * gstFactor;
        
        const monthYear = `${year}-${month.toString().padStart(2, '0')}`;
        accommodationOccupancyData.labels.push(monthYear);
        accommodationOccupancyData.datasets[0].data.push(totalRevenue);
        accommodationOccupancyData.datasets[1].data.push(bookingCount);
    });

    roomTypeData.forEach(item => {
        const roomType = item[0];
        const bookingCount = item[1];
        const bookingAmount = parseFloat(item[3]) * gstFactor;
        accommodationRoomTypeData.labels.push(roomType);
        accommodationRoomTypeData.datasets[0].data.push(bookingCount);
        accommodationRoomTypeData.revenueData.push(bookingAmount);
    });
}

function populateAccommodationYearSelector() {
    const years = [...new Set(monthlyAccommodationData.map(item => item[0]))];
    const yearSelector = document.getElementById('accommodationYearSelector');
    years.forEach(year => {
        const option = document.createElement('option');
        option.value = year;
        option.text = year;
        if (year == new Date().getFullYear()) {
            option.selected = true;
        }   
        yearSelector.appendChild(option);
    });
}

function updateAccommodationCharts() {
    const selectedYear = document.getElementById('accommodationYearSelector').value;
    const filteredMonthlyData = monthlyAccommodationData.filter(item => item[0] == selectedYear);
    const filteredRoomTypeData = roomTypeDistributionData.filter(item => item[2] == selectedYear);
    createAccommodationCharts(filteredMonthlyData, filteredRoomTypeData);
}

function createAccommodationCharts(filteredMonthlyData, filteredRoomTypeData) {
    if (!filteredMonthlyData || filteredMonthlyData.length === 0) {
        console.error("Accommodation data is not loaded");
        return;
    }

    if (occupancyBarChart) {
        occupancyBarChart.destroy();
    }
    if (roomTypePieChart) {
        roomTypePieChart.destroy();
    }

    processAccommodationData(filteredMonthlyData, filteredRoomTypeData);

    const barChartCanvas = document.getElementById('monthlyOccupancyBarChart').getContext('2d');
    occupancyBarChart = new Chart(barChartCanvas, {
        type: 'bar',
        data: accommodationOccupancyData,
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
                y1: {
                    beginAtZero: true,
                    position: 'right',
                    grid: {
                        drawOnChartArea: false,
                    },
                    title: {
                        display: true,
                        text: 'Booking Count',
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
                    displayColors: false,
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (context.datasetIndex === 0) {
                                // Revenue
                                label = 'Revenue: $' + context.raw.toFixed(2);
                            } else {
                                // Booking Count
                                label = 'Booking Count: ' + context.raw;
                            }
                            return label;
                        },
                        afterLabel: function(context) {
                            if (context.datasetIndex === 0) {
                                // Revenue
                                label = 'Booking Count: ' + accommodationOccupancyData.datasets[1].data[context.dataIndex];
                            } else {
                                // Booking Count
                                label = 'Revenue: $' + accommodationOccupancyData.datasets[0].data[context.dataIndex].toFixed(2);
                            }
                            return label;
                        }
                    }
                }
            },
        }
    });

    const pieChartCanvas = document.getElementById('roomTypePieChart').getContext('2d');
    roomTypePieChart = new Chart(pieChartCanvas, {
        type: 'pie',
        data: accommodationRoomTypeData,
        options: {
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = accommodationRoomTypeData.labels[context.dataIndex] || '';
                            let count = accommodationRoomTypeData.datasets[0].data[context.dataIndex];
                            let revenue = accommodationRoomTypeData.revenueData[context.dataIndex].toFixed(2);
                            return label + ': ' + count + ', Revenue $' + revenue;
                        }
                    }
                }
            }
        }
    });
}
