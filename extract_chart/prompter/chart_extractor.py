"""
Chart extraction module using OpenAI Vision via LangChain.
"""

import base64
import json
import sys
from pathlib import Path
from typing import Dict, Optional

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage


def encode_image(image_path: Path) -> str:
    """Encode image to base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def extract_chart_coordinates(image_path: Path, api_key: Optional[str] = None) -> Dict:
    """
    Extract approximate coordinates of the main chart from an image.
    
    Args:
        image_path: Path to the PNG image file
        api_key: OpenAI API key (if not provided, uses OPENAI_API_KEY env var)
    
    Returns:
        Dictionary containing chart coordinates and metadata
    """
    # Validate image file exists
    if not image_path.exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")
    
    if image_path.suffix.lower() not in ['.png', '.jpg', '.jpeg']:
        raise ValueError(f"Unsupported image format: {image_path.suffix}. Use PNG, JPG, or JPEG.")
    
    # Initialize LangChain ChatOpenAI with vision model
    # API key can be passed directly or via OPENAI_API_KEY environment variable
    llm_kwargs = {
        "model": "gpt-4o",  # or "gpt-4-vision-preview" for older models
        "temperature": 0
    }
    if api_key:
        llm_kwargs["api_key"] = api_key
    
    # Use GPT-4 Vision model
    llm = ChatOpenAI(**llm_kwargs)
    
    # Encode image
    base64_image = encode_image(image_path)
    
    # Create prompt asking for chart coordinates
    prompt = """Analyze this screenshot image and identify the main chart or graph displayed.

Please provide the approximate coordinates of the chart area in the following format:
- x: left edge of the chart (in pixels from left)
- y: top edge of the chart (in pixels from top)
- width: width of the chart area (in pixels)
- height: height of the chart area (in pixels)

Also provide:
- chart_type: type of chart (e.g., "line chart", "bar chart", "scatter plot", etc.)
- confidence: your confidence level (0-1) that this is the main chart

Return the response as a JSON object with these fields: x, y, width, height, chart_type, confidence.
If you cannot identify a chart, return null values with confidence 0."""
    
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
    
    # Get response from model
    print(f"Analyzing image: {image_path}", file=sys.stderr)
    response = llm.invoke([message])
    
    # Parse response
    response_text = response.content.strip()
    
    # Try to extract JSON from response
    try:
        # Look for JSON in the response (might be wrapped in markdown code blocks)
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            json_str = response_text[json_start:json_end].strip()
        elif "```" in response_text:
            json_start = response_text.find("```") + 3
            json_end = response_text.find("```", json_start)
            json_str = response_text[json_start:json_end].strip()
        else:
            json_str = response_text
        
        # Try to find JSON object in the text
        json_start = json_str.find("{")
        json_end = json_str.rfind("}") + 1
        if json_start >= 0 and json_end > json_start:
            json_str = json_str[json_start:json_end]
        
        coordinates = json.loads(json_str)
        return coordinates
    except json.JSONDecodeError as e:
        print(f"Warning: Could not parse JSON from response: {e}", file=sys.stderr)
        print(f"Raw response: {response_text}", file=sys.stderr)
        # Return raw response as fallback
        return {
            "raw_response": response_text,
            "error": "Failed to parse JSON response"
        }


