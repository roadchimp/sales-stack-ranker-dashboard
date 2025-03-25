// Fetch and display sales data
async function fetchSalesData() {
    try {
        const response = await fetch('/api/sales-data');
        const data = await response.json();
        updateSalesChart(data.sales);
    } catch (error) {
        console.error('Error fetching sales data:', error);
    }
}

// Update the sales rank chart
function updateSalesChart(salesData) {
    const ctx = document.getElementById('sales-rank-chart');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: salesData.map(item => item.name),
            datasets: [{
                label: 'Sales Value',
                data: salesData.map(item => item.value),
                backgroundColor: 'rgba(59, 130, 246, 0.5)',
                borderColor: 'rgb(59, 130, 246)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Sales Value ($)'
                    }
                }
            }
        }
    });
}

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    fetchSalesData();
}); 