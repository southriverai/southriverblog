"""
Pydantic models for chart metadata extraction using LangChain.
These models define the structure for extracting chart information from images.
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class AxisMetadata(BaseModel):
    """Metadata for a chart axis."""
    
    label: Optional[str] = Field(
        None,
        description="The label or title of the axis"
    )
    ticks: Optional[List[float]] = Field(
        None,
        description="List of tick values displayed on the axis"
    )
    scale_type: Literal["linear", "log", "log10", "log2", "sqrt", "date", "category"] = Field(
        "linear",
        description="The scale type of the axis (linear, log, etc.)"
    )
    is_log_scale: bool = Field(
        False,
        description="Whether the axis uses a logarithmic scale"
    )
    min_value: Optional[float] = Field(
        None,
        description="The minimum value shown on the axis"
    )
    max_value: Optional[float] = Field(
        None,
        description="The maximum value shown on the axis"
    )
    unit: Optional[str] = Field(
        None,
        description="The unit of measurement for the axis (e.g., 'years', 'dollars', 'percentage')"
    )


class SeriesMetadata(BaseModel):
    """Metadata for a line series in the chart."""
    
    name: str = Field(
        ...,
        description="The name or label of the line series"
    )
    color: Optional[str] = Field(
        None,
        description="The color of the line series (if identifiable)"
    )
    # Note: We don't include actual data values, only metadata


class ChartMetadata(BaseModel):
    """Complete metadata structure for a line chart extracted from an image."""
    
    title: Optional[str] = Field(
        None,
        description="The main title of the chart"
    )
    
    subtitle: Optional[str] = Field(
        None,
        description="Subtitle or secondary title if present"
    )
    
    x_axis: AxisMetadata = Field(
        ...,
        description="Metadata for the X-axis"
    )
    
    y_axis: AxisMetadata = Field(
        ...,
        description="Metadata for the Y-axis"
    )
    
    series: List[SeriesMetadata] = Field(
        default_factory=list,
        description="List of all data series in the chart with their metadata"
    )
    
    has_legend: bool = Field(
        False,
        description="Whether the chart has a legend"
    )
    
    legend_position: Optional[Literal["top", "bottom", "left", "right", "top-left", "top-right", "bottom-left", "bottom-right"]] = Field(
        None,
        description="Position of the legend if present"
    )
    
    has_grid: bool = Field(
        False,
        description="Whether the chart has grid lines"
    )
    
    grid_direction: Optional[Literal["both", "horizontal", "vertical"]] = Field(
        None,
        description="Direction of grid lines if present"
    )

    data_source: Optional[str] = Field(
        None,
        description="Source or attribution of the data if visible in the chart"
    )
    
    notes: Optional[str] = Field(
        None,
        description="Any additional notes or annotations visible on the chart"
    )
    
    confidence: float = Field(
        0.0,
        ge=0.0,
        le=1.0,
        description="Confidence level (0-1) in the extracted metadata"
    )
