# Chart Coordinate Extraction Script

This script uses OpenAI's vision model (via LangChain) to analyze a screenshot image and extract the approximate coordinates of the main chart displayed in the image.

## Installation

1. Install required packages:
```bash
pip install -r requirements.txt
```

2. Set your OpenAI API key:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

Or pass it via the `--api-key` argument.

## Usage

### Basic usage:
```bash
python extract_chart_coordinates.py screenshot.png
```

### Save output to file:
```bash
python extract_chart_coordinates.py screenshot.png --output coordinates.json
```

### With API key as argument:
```bash
python extract_chart_coordinates.py screenshot.png --api-key "your-api-key"
```

## Output Format

The script returns a JSON object with the following fields:

```json
{
  "x": 100,
  "y": 200,
  "width": 800,
  "height": 500,
  "chart_type": "line chart",
  "confidence": 0.95
}
```

- `x`: Left edge of the chart (pixels from left)
- `y`: Top edge of the chart (pixels from top)
- `width`: Width of the chart area (pixels)
- `height`: Height of the chart area (pixels)
- `chart_type`: Type of chart identified
- `confidence`: Confidence level (0-1)

## Example

```bash
python extract_chart_coordinates.py plot_screenshot.png --output chart_coords.json
```

This will analyze the image and save the coordinates to `chart_coords.json`.

