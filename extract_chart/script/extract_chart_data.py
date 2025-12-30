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
from typing import Optional, List
from typing import Tuple
#from southriverblog.model.chart_prompt_model import ChartData
from southriverblog.model.chart_prompt_model import ChartMetadata

import numpy as np
from PIL import Image
import cv2


def get_horizontal_line_coordinates_0(image_binary: np.array) -> Tuple[int, int]:
    cv2.imshow("Thresholded Image", image_binary)

    if image_binary.shape[0] == 0:
        raise ValueError("Image binary is empty")
    if image_binary.shape[1] == 0:
        raise ValueError("Image binary is empty")
    # given a binary image, of a horizontal line, begining and end of the line by estimating it as a uniform distribution
    # return the beginning and end of the line as a tuple
    print(image_binary.shape)
    histogram = np.sum(image_binary, axis=0)
    histogram = histogram / np.sum(histogram)
    cum_sum = np.cumsum(histogram)
    print(cum_sum)
    for i in range(len(histogram)):
        if cum_sum[i] > 0.25:
            p_25 = i
            break
    for i in range(len(histogram)):
        if cum_sum[i] > 0.75:
            p_75 = i
            break
    # find the 1st and last quantiles of the histogram
    mean = (p_25 + p_75) / 2
    print(p_25, p_75, mean)
    beginning = int(mean - (p_75 - p_25) * 0.5)
    end = int(mean + (p_75 - p_25) * 0.5)
    print(beginning, end)
    return beginning, end



def get_horizontal_line_coordinates_cc(image_binary: np.array) -> Tuple[int, int]:
    # find the min x and the max x of the biggest connected
    num_labels, labels = cv2.connectedComponents(255 - image_binary)

    # Check if we have any components (excluding background)
    if num_labels <= 1:
        # No white pixels found, return full width
        return 0, image_binary.shape[1] - 1
    
    # Find the size of each component (excluding background label 0)
    component_sizes = []
    for label in range(1, num_labels):  # Skip background (label 0)
        component_mask = labels == label
        component_size = np.sum(component_mask)
        component_sizes.append((label, component_size))

    if not component_sizes:
        # No components found, return full width
        return 0, image_binary.shape[1] - 1

    # Find the biggest component
    biggest_label, _ = max(component_sizes, key=lambda x: x[1])
    biggest_component_mask = labels == biggest_label
    # Get x coordinates of the biggest component
    x_coords = np.where(biggest_component_mask)[1]
    if len(x_coords) == 0:
        # No pixels found in biggest component, return full width
        return 0, image_binary.shape[1] - 1

    min_x = int(np.min(x_coords))
    max_x = int(np.max(x_coords))
    return min_x, max_x

def extract_chart_area(image_array: np.array) -> np.array:
    #TODO remove all text from the image
    # convert the image to grayscale
    image_array_gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)

    # if this image is mayorety dark, invert the image
    if np.mean(image_array_gray) < 127:
        image_array_gray = 255 - image_array_gray

    # apply a threshold to the image
    _, image_array_threshold = cv2.threshold(image_array_gray, 240, 255, cv2.THRESH_BINARY)


    # find the bottom line in the image by making histogram of the image and finding the bottom most line
    # Create histogram with one bin per row (line) - sum white pixels in each row
    histogram = np.sum(image_array_threshold, axis=1)  # Sum white pixels in each row
    bottom_line_center = int(np.argmin(histogram)) #TODO make this more robust
    # crop out the area 1% above and below the bottom line
    offset = max(1, int(image_array_threshold.shape[0] * 0.01))
    bottom_line_top = int(bottom_line_center - offset)
    bottom_line_bottom = int(bottom_line_center + offset)

    # crop the image to the bottom line
    image_bottom_line = image_array_threshold[bottom_line_top:bottom_line_bottom, :]
    cv2.imshow("Image Bottom Line", image_bottom_line)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    beginning, end = get_horizontal_line_coordinates_cc(image_bottom_line)
    # draw these as black vertical lines on the image
    # cv2.line(image_array_threshold, (beginning, bottom_line_top), (beginning, image_array_threshold.shape[0]), (0, 0, 0), 2)
    # cv2.line(image_array_threshold, (end, bottom_line_top), (end, image_array_threshold.shape[0]), (0, 0, 0), 2)
    # cv2.imshow("Image with Lines", image_array_threshold)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # crop the image to the bottom line
    image_array = image_array[:bottom_line_center, beginning:end,:]
    return image_array

def crop_line(line: tuple, image_array: np.array) -> tuple:
    # crop the line to the image array
    line = list(line)   # convert the line to a list
    line[0] = max(0, line[0])
    line[1] = max(0, line[1])
    line[2] = min(line[2], image_array.shape[1])
    line[3] = min(line[3], image_array.shape[0])
    return tuple(line)  # convert the list back to a tuple

def extract_series_colors(image_array: np.array, series_count:int) -> List[Tuple[int, int, int]]:
    # show the image
    cv2.imshow("Image", image_array)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    """
    Extract series colors from a chart image using HSV color space histogram.
    
    Args:
        image_array: BGR image array from OpenCV
        
    Returns:
        List of RGB color tuples representing the series colors
    """
    # Convert BGR to HSV color space
    print(image_array.shape)
    hsv_image = cv2.cvtColor(image_array, cv2.COLOR_BGR2HSV)
    
    # Create a 2D histogram in HSV space (Hue and Saturation)
    # Hue: 0-179 (OpenCV uses 0-179 for hue)
    # Saturation: 0-255
    hist = cv2.calcHist(
        [hsv_image],
        [0],  # Use Hue and Saturation channels
        None,
        [180],  # 180 bins for Hue, 256 for Saturation
        [0, 180]
    )
    # show the histogram
    cv2.imshow("Histogram", hist)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # use sklearn to find the peaks in the histogram
    # import library
    from findpeaks import findpeaks

    # Find some peaks using the smoothing parameter.
    fp = findpeaks(lookahead=1, interpolate=10)
    # fit
    results = fp.fit(hist)
    print(results)
    colors = []
    for peak in peaks:
        colors.append(hsv_image[peak[0], peak[1]])
    print(colors)
    return colors



def extract_series(image_array: np.array, colors: List[Tuple[int, int, int]]) -> List[List[float]]:
    # extract the series from the image and
    series = []
    for color in colors:
        # create a mask for the color
        mask = cv2.inRange(image_array, color, color)
        # extract the series from the mask
        series = image_array[mask == 255]
        print(series.shape)
        # extract the x and y coordinates of the series
        x_coords = series[:, 0]
        y_coords = series[:, 1]
        # return the x and y coordinates as a list of tuples
        return list(zip(x_coords, y_coords))
    return series


def extract_chart_data(image_path: Path, chart_metadata: ChartMetadata) -> None:
    # convert the image to a numpy array
    image = Image.open(image_path)
    image_array = np.array(image)
    # rescale to 50% of the original size
    image_array = cv2.resize(image_array, (int(image_array.shape[1] * 0.5), int(image_array.shape[0] * 0.5)))

    image_array_chart = extract_chart_area(image_array)
    colors = extract_series_colors(image_array_chart, 3)
    series = extract_series(image_array_chart, colors)
    print(series)





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
        metadata = extract_chart_data(image_path, None)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

