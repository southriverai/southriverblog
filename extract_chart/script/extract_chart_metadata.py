#!/usr/bin/env python3
"""
Script to extract chart metadata from an image using LangChain and GPT-4o vision model.
Uses structured output to return ChartMetadata model.
"""

import argparse
import base64
import json
import sys
from pathlib import Path
from typing import Optional

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from southriverblog.model.chart_prompt_model import ChartMetadata


def encode_image(image_path: Path) -> str:
    """Encode image to base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def extract_chart_metadata(image_path: Path) -> ChartMetadata:
    """
    Extract chart metadata from an image using GPT-4o vision model with structured output.
    
    Args:
        image_path: Path to the PNG/JPG image file
        api_key: OpenAI API key (if not provided, uses OPENAI_API_KEY env var)
    
    Returns:
        ChartMetadata object containing all extracted metadata
    """
    # Validate image file exists
    if not image_path.exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")
    
    if image_path.suffix.lower() not in ['.png', '.jpg', '.jpeg']:
        raise ValueError(f"Unsupported image format: {image_path.suffix}. Use PNG, JPG, or JPEG.")
    
    # Initialize LangChain ChatOpenAI with vision model
    import os
    llm = ChatOpenAI(
        model="gpt-4o",
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0
    )
    
    # Create LLM with structured output
    structured_llm = llm.with_structured_output(ChartMetadata)
    
    # Encode image
    base64_image = encode_image(image_path)
    
    # Create prompt asking for chart metadata
    prompt = """Analyze this line chart image and extract all metadata about the chart.

Please provide:
- Title and subtitle (if present)
- X-axis: label, tick values, scale type (linear/log), min/max values, unit
- Y-axis: label, tick values, scale type (linear/log), min/max values, unit
- All series: names and colors (if identifiable)
- Legend: whether present and its position
- Grid: whether present and direction
- Data source: if visible in the chart
- Notes: any additional annotations or notes
- Confidence: your confidence level (0-1) in the extracted metadata

IMPORTANT: Do NOT extract the actual data values. Only extract metadata about:
- What the axes represent (labels, units, scale types)
- What tick marks are shown
- What series are present (names only, not data points)
- Visual elements like legend, grid, etc.

For axis ticks, provide the actual tick values you can see on the chart.
For scale types, determine if axes are linear or logarithmic based on the spacing of tick marks.
For series, list all line series visible in the chart with their names."""
    
    # Create message with image
    message = HumanMessage(
        content=[
            {
                "type": "text",
                "text": prompt
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{base64_image}"
                }
            }
        ]
    )
    
    # Get structured response from model
    print(f"Analyzing chart image: {image_path}", file=sys.stderr)
    metadata = structured_llm.invoke([message])
    
    return metadata


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Extract chart metadata from a line chart image using GPT-4o vision model"
    )
    parser.add_argument(
        "image_path",
        type=str,
        help="Path to the PNG/JPG image file containing a line chart"
    )

    args = parser.parse_args()
    
    try:
        image_path = Path(args.image_path)
        
        # Extract metadata using LLM
        print("Extracting chart metadata using OpenAI Vision...", file=sys.stderr)
        metadata = extract_chart_metadata(image_path)
        
        # Convert to dict for JSON serialization
        metadata_dict = metadata.model_dump()
        
        # Output metadata as pretty JSON
        metadata_json = json.dumps(metadata_dict, indent=2, ensure_ascii=False)
        print("\nExtracted metadata:", file=sys.stderr)
        print(metadata_json)
        
        print(f"\nConfidence: {metadata.confidence:.2f}", file=sys.stderr)
        print(f"Series found: {len(metadata.series)}", file=sys.stderr)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

