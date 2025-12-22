/**
 * Chart Viewer Component
 * Handles loading and rendering the Plotly chart
 */

class ChartViewer {
    constructor(containerId) {
        this.containerId = containerId;
        this.chartLoaded = false;
    }

    /**
     * Initialize and render the chart
     */
    async init() {
        // Ensure Plotly is loaded
        if (typeof Plotly === 'undefined') {
            console.error('Plotly.js is not loaded');
            this.showError('Error: Plotly.js library failed to load.');
            return;
        }

        // Ensure loadChartData function is available
        if (typeof loadChartData === 'undefined') {
            console.error('loadChartData function is not defined');
            this.showError('Error: plot-config.js failed to load.');
            return;
        }

        try {
            // Load data and render the plot
            const { plotData, plotLayout, plotConfig } = await loadChartData();
            const container = document.getElementById(this.containerId);
            
            if (!container) {
                console.error(`Container with id "${this.containerId}" not found`);
                return;
            }

            Plotly.newPlot(this.containerId, plotData, plotLayout, plotConfig);
            this.chartLoaded = true;
        } catch (error) {
            console.error('Failed to load chart:', error);
            this.showError(
                'Error loading chart data. Please check the console for details.<br>' +
                'Note: If opening the file directly, you may need to use a local server due to CORS restrictions.'
            );
        }
    }

    /**
     * Show an error message
     */
    showError(message) {
        const container = document.getElementById(this.containerId);
        if (container) {
            container.innerHTML = `<p style="color: red; padding: 20px;">${message}</p>`;
        }
    }

    /**
     * Check if chart has been loaded
     */
    isLoaded() {
        return this.chartLoaded;
    }
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ChartViewer;
}

