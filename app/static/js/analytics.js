document.addEventListener('DOMContentLoaded', function () {
    const ctx = document.getElementById('salesChart');
    const salesDataTable = document.getElementById('sales-data-table');

    if (ctx) {
        async function renderChartAndTable() {
            try {
                const response = await fetch('/api/analytics/sales-over-time');
                if (!response.ok) throw new Error('Could not fetch sales data from the server.');
                
                const salesData = await response.json();

                new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: salesData.labels,
                        datasets: [{
                            label: 'Total Sales (₹)',
                            data: salesData.data,
                            borderColor: '#38bdf8',
                            backgroundColor: 'rgba(56, 189, 248, 0.2)',
                            fill: true,
                            tension: 0.4
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            y: { beginAtZero: true, ticks: { color: '#9ca3af' }, grid: { color: '#374151' } },
                            x: { ticks: { color: '#9ca3af' }, grid: { color: '#374151' } }
                        },
                        plugins: {
                            legend: { labels: { color: '#d1d5db' } }
                        }
                    }
                });

                if (salesDataTable) {
                    salesDataTable.innerHTML = '';
                    salesData.labels.forEach((label, index) => {
                        const row = document.createElement('tr');
                        row.className = 'border-t border-slate-700';
                        row.innerHTML = `<td class="h-[72px] px-4 py-2 text-slate-400 text-sm">${label}</td><td class="h-[72px] px-4 py-2 text-slate-400 text-sm">₹${salesData.data[index].toFixed(2)}</td>`;
                        salesDataTable.appendChild(row);
                    });
                }
            } catch (error) {
                console.error('Chart rendering error:', error);
                ctx.parentElement.innerHTML = `<p class="text-red-400 text-center">${error.message}</p>`;
            }
        }
        renderChartAndTable();
    }
});