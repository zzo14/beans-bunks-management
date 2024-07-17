document.addEventListener("DOMContentLoaded", function() {
    populateFinalcialYearSelector();
    updateFinancialCharts();
});

const barChartData = {
    labels: [],
    datasets: []
};

const pieChartData = {
    labels: [],
    datasets: [{
        data: [],
        backgroundColor: [
            '#C19A6B', // light brown
            '#6F4E37', // brown
            '#F4E1C1', // light tan
            '#8B4513',  // bronze
            '#CD853F',  // peru
        ],
    }],
};
let barChartInstance = null;
let pieChartInstance = null;

function resetData() {
    barChartData.labels = [];
    barChartData.datasets = [];
    pieChartData.labels = [];  
    pieChartData.datasets[0].data = [];
    pieChartData.datasets[0].backgroundColor = [
        '#C19A6B', // light brown
        '#6F4E37', // brown
        '#F4E1C1', // light tan
        '#8B4513',  // bronze
        '#CD853F',  // peru
    ];
}

function processFinancialData(financialReportData) {
    resetData();
    const monthlyData = {};
    const typeData = {};

    const includeGST = document.getElementById('financialIncludeGST').checked;
    const gstFactor = includeGST ? 1 : 0.85;

    financialReportData.forEach(item => {
      const monthYear = `${item[0]}-${item[1].toString().padStart(2, '0')}`;
      const type = item[2].charAt(0).toUpperCase() + item[2].slice(1);
      const revenue = parseFloat(item[3]) * gstFactor;

      if (!monthlyData[monthYear]) {
        monthlyData[monthYear] = {};
        barChartData.labels.push(monthYear);
      }
      if (!monthlyData[monthYear][type]) {
        monthlyData[monthYear][type] = 0;
      }
      monthlyData[monthYear][type] += revenue;

      if (!typeData[type]) {
        typeData[type] = 0;
        pieChartData.labels.push(type);
      }
      typeData[type] += revenue;
    });

    Object.keys(typeData).forEach((type, index) => {
      const color = pieChartData.datasets[0].backgroundColor[index % pieChartData.datasets[0].backgroundColor.length];
      const data = barChartData.labels.map(monthYear => (monthlyData[monthYear] && monthlyData[monthYear][type]) ? monthlyData[monthYear][type] : 0);
      barChartData.datasets.push({ label: type, data: data, backgroundColor: color, maxBarThickness: 75 });
    });

    pieChartData.datasets[0].data = pieChartData.labels.map(type => typeData[type]);
  }

  function populateFinalcialYearSelector() {
    const years = [...new Set(financialReportData.map(item => item[0]))];
    const yearSelector = document.getElementById('financialYearSelector');
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

  function updateFinancialCharts() {
    const selectedYear = document.getElementById('financialYearSelector').value;
    const filteredData = financialReportData.filter(item => item[0] == selectedYear);
    createFinanicalCharts(filteredData);
  }

  function createFinanicalCharts(filteredData) {
    if (!filteredData || filteredData.length === 0) {
      console.error("Financial report data is not loaded");
      return;
    }

    if (barChartInstance) {
      barChartInstance.destroy();
    }
    if (pieChartInstance) {
      pieChartInstance.destroy();
    }

    processFinancialData(filteredData);

    const barChartCanvas = document.getElementById('monthlyRevenueBarChart').getContext('2d');
    barChartInstance = new Chart(barChartCanvas, {
      type: 'bar',
      data: barChartData,
      options: {
        scales: {
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: 'Revenue',
              font: {
                weight: 'bold'
              }
            },
            ticks: {
              callback: function(value) {
                return '$' + value;
              }
            }
          }
        },
        plugins: {
          tooltip: {
            callbacks: {
              label: function(context) {
                let label = context.dataset.label || '';
                if (label) {
                  label += ': ';
                }
                label += '$' + context.raw.toFixed(2);
                return label;
              }
            }
          }
        },
      }
    });

    const pieChartCanvas = document.getElementById('annualRevenuePieChart').getContext('2d');
    pieChartInstance = new Chart(pieChartCanvas, {
      type: 'pie',
      data: pieChartData,
      options: {
        plugins: {
          tooltip: {
            callbacks: {
              label: function(context) {
                let label = pieChartData.labels[context.dataIndex] || '';
                if (label) {
                  label += ': ';
                }
                label += '$' + context.parsed.toFixed(2);
                return label;
              }
            }
          }
        }
      }
    });

    updateTotalRevenue();
  }

  function updateTotalRevenue() {
    const totalRevenue = pieChartData.datasets[0].data.reduce((total, value) => total + Number(value), 0);
    document.getElementById('annualTotalRevenue').textContent = "Total Revenue: $" + totalRevenue.toFixed(2);
  }