// Plotly chart configuration and data
// This file loads data from data.json and creates the chart configuration

// Colors for the three series
const seriesColors = [
    'rgb(102, 126, 234)',  // Blue
    'rgb(118, 75, 162)',   // Purple
    'rgb(255, 99, 132)'    // Pink/Red
];

// Function to load data and create chart configuration
async function loadChartData() {
    try {
        // Fetch data from data.json
        const response = await fetch('data.json');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        
        // Create traces from the series data
        const plotData = data.series.map((series, index) => ({
            x: data.years,
            y: series.data,
            type: 'scatter',
            mode: 'lines+markers',
            name: series.name,
            line: {
                color: seriesColors[index % seriesColors.length],
                width: 3
            },
            marker: {
                size: 10,
                color: seriesColors[index % seriesColors.length]
            }
        }));
        
        // Layout configuration using metadata from JSON
        const plotLayout = {
            title: {
                text: data.title,
                font: {
                    size: 24,
                    color: '#333'
                }
            },
            xaxis: {
                title: data.xAxisLabel,
                titlefont: {
                    size: 14,
                    color: '#666'
                },
                tickfont: {
                    size: 12
                }
            },
            yaxis: {
                title: data.yAxisLabel,
                titlefont: {
                    size: 14,
                    color: '#666'
                },
                tickfont: {
                    size: 12
                }
            },
            hovermode: 'closest',
            plot_bgcolor: 'white',
            paper_bgcolor: 'white',
            legend: {
                x: 0.7,
                y: 0.95,
                bgcolor: 'rgba(255, 255, 255, 0.8)',
                bordercolor: '#ddd',
                borderwidth: 1
            },
            margin: {
                l: 60,
                r: 40,
                t: 60,
                b: 50
            }
        };
        
        // Plot configuration
        const plotConfig = {
            responsive: true,
            displayModeBar: true,
            displaylogo: false,
            modeBarButtonsToRemove: ['pan2d', 'lasso2d']
        };
        
        return { plotData, plotLayout, plotConfig };
    } catch (error) {
        console.error('Error loading chart data:', error);
        throw error;
    }
}
