document.addEventListener('DOMContentLoaded', function() {
    // Configuration Chart.js
    Chart.defaults.font.family = 'Inter, sans-serif';
    Chart.defaults.font.size = 12;
    Chart.defaults.color = '#94a3b8';
    Chart.defaults.plugins.legend.labels.color = '#cbd5e1';
    
    // Récupération des statistiques
    fetch('/dashboard/api/stats')
        .then(response => response.json())
        .then(data => {
            // Graphique Distribution des Attaques
            const attackCtx = document.getElementById('attackChart');
            if (attackCtx) {
                const attackLabels = Object.keys(data.label_distribution);
                const attackData = Object.values(data.label_distribution);
                
                new Chart(attackCtx, {
                    type: 'bar',
                    data: {
                        labels: attackLabels,
                        datasets: [{
                            label: 'Nombre de logs',
                            data: attackData,
                            backgroundColor: '#3b82f6',
                            borderRadius: 6,
                            borderSkipped: false,
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: true,
                        plugins: {
                            legend: {
                                display: false
                            },
                            tooltip: {
                                backgroundColor: 'rgba(15, 23, 42, 0.95)',
                                padding: 12,
                                cornerRadius: 8,
                                titleColor: '#f1f5f9',
                                bodyColor: '#cbd5e1',
                                borderColor: '#334155',
                                borderWidth: 1
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                grid: {
                                    color: '#334155',
                                    drawBorder: false
                                },
                                ticks: {
                                    color: '#94a3b8',
                                    padding: 8
                                }
                            },
                            x: {
                                grid: {
                                    display: false,
                                    drawBorder: false
                                },
                                ticks: {
                                    color: '#94a3b8',
                                    padding: 8
                                }
                            }
                        }
                    }
                });
            }
            
            // Graphique Statut des Alertes
            const statusCtx = document.getElementById('statusChart');
            if (statusCtx) {
                const statusLabels = Object.keys(data.status_distribution);
                const statusData = Object.values(data.status_distribution);
                
                new Chart(statusCtx, {
                    type: 'doughnut',
                    data: {
                        labels: statusLabels.map(s => s.charAt(0).toUpperCase() + s.slice(1)),
                        datasets: [{
                            data: statusData,
                            backgroundColor: [
                                '#ef4444',
                                '#f59e0b',
                                '#10b981'
                            ],
                            borderColor: '#1e293b',
                            borderWidth: 3,
                            hoverOffset: 8
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: true,
                        cutout: '65%',
                        plugins: {
                            legend: {
                                position: 'bottom',
                                labels: {
                                    padding: 15,
                                    color: '#cbd5e1',
                                    font: {
                                        size: 12,
                                        weight: '500'
                                    },
                                    usePointStyle: true,
                                    pointStyle: 'circle'
                                }
                            },
                            tooltip: {
                                backgroundColor: 'rgba(15, 23, 42, 0.95)',
                                padding: 12,
                                cornerRadius: 8,
                                titleColor: '#f1f5f9',
                                bodyColor: '#cbd5e1',
                                borderColor: '#334155',
                                borderWidth: 1
                            }
                        }
                    }
                });
            }
        })
        .catch(error => console.error('Erreur chargement stats:', error));
});