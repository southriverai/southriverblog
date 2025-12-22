#!/usr/bin/env python3
"""
Script to extract chart coordinates from a screenshot and crop the chart to a separate image file.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from PIL import Image

from soutriverblog import extract_chart_coordinates


def crop_chart(
    image_path: Path,
    coordinates: dict,
    output_path: Optional[Path] = None
) -> Path:
    """
    Crop the chart from the image using the provided coordinates.
    
    Args:
        image_path: Path to the source image
        coordinates: Dictionary with x, y, width, height
        output_path: Path to save the cropped image (default: adds '_chart' suffix)
    
    Returns:
        Path to the saved cropped image
    """
    # Validate coordinates
    required_fields = ['x', 'y', 'width', 'height']
    if not all(field in coordinates for field in required_fields):
        raise ValueError(f"Missing required coordinate fields: {required_fields}")
    
    if any(coordinates[field] is None for field in required_fields):
        raise ValueError("One or more coordinate values are None")
    
    x = int(coordinates['x'])
    y = int(coordinates['y'])
    width = int(coordinates['width'])
    height = int(coordinates['height'])
    
    # Validate coordinates are non-negative
    if x < 0 or y < 0 or width <= 0 or height <= 0:
        raise ValueError(f"Invalid coordinates: x={x}, y={y}, width={width}, height={height}")
    
    # Open the image
    print(f"Opening image: {image_path}", file=sys.stderr)
    img = Image.open(image_path)
    img_width, img_height = img.size
    
    # Validate coordinates are within image bounds
    if x + width > img_width:
        print(f"Warning: x + width ({x + width}) exceeds image width ({img_width}), adjusting...", file=sys.stderr)
        width = img_width - x
    
    if y + height > img_height:
        print(f"Warning: y + height ({y + height}) exceeds image height ({img_height}), adjusting...", file=sys.stderr)
        height = img_height - y
    
    # Crop the image
    print(f"Cropping chart at ({x}, {y}) with size {width}x{height}", file=sys.stderr)
    cropped_img = img.crop((x, y, x + width, y + height))
    
    # Determine output path
    if output_path is None:
        stem = image_path.stem
        suffix = image_path.suffix
        output_path = image_path.parent / f"{stem}_chart{suffix}"
    
    # Save the cropped image
    print(f"Saving cropped chart to: {output_path}", file=sys.stderr)
    cropped_img.save(output_path)
    
    return output_path


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Extract chart coordinates from a screenshot and crop the chart to a separate image"
    )
    parser.add_argument(
        "image_path",
        type=str,
        help="Path to the PNG/JPG image file"
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default=None,
        help="OpenAI API key (or set OPENAI_API_KEY environment variable)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output image file path for cropped chart (default: adds '_chart' suffix to input filename)"
    )
    parser.add_argument(
        "--coordinates-output",
        type=str,
        default=None,
        help="Output JSON file path for coordinates (default: print to stdout)"
    )
    parser.add_argument(
        "--skip-crop",
        action="store_true",
        help="Skip cropping and only extract coordinates"
    )

    args = parser.parse_args()
    
    try:
        image_path = Path(args.image_path)
        
        # Step 1: Extract coordinates using LLM
        print("Step 1: Extracting chart coordinates using OpenAI Vision...", file=sys.stderr)
        coordinates = extract_chart_coordinates(
            image_path,
            api_key=args.api_key
        )
        
        # Check for errors
        if "error" in coordinates:
            print(f"Error extracting coordinates: {coordinates.get('error')}", file=sys.stderr)
            if "raw_response" in coordinates:
                print(f"Raw response: {coordinates['raw_response']}", file=sys.stderr)
            sys.exit(1)
        
        # Output coordinates
        coordinates_json = json.dumps(coordinates, indent=2)
        if args.coordinates_output:
            with open(args.coordinates_output, 'w') as f:
                f.write(coordinates_json)
            print(f"Coordinates saved to: {args.coordinates_output}", file=sys.stderr)
        else:
            print("Extracted coordinates:", file=sys.stderr)
            print(coordinates_json)
        
        # Step 2: Crop the chart if not skipped
        if not args.skip_crop:
            print("\nStep 2: Cropping chart from image...", file=sys.stderr)
            output_path = Path(args.output) if args.output else None
            cropped_path = crop_chart(image_path, coordinates, output_path)
            print(f"\nSuccess! Cropped chart saved to: {cropped_path}", file=sys.stderr)
        else:
            print("\nSkipping crop step (--skip-crop flag set)", file=sys.stderr)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
