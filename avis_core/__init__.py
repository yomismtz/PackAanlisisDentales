"""Núcleo puro de dominio de AVIS, independiente de las interfaces."""

from .geometry import (
    bilateral_difference,
    line_angle_difference_degrees,
    line_inclination_degrees,
    segment_proportions_percent,
)

__all__ = [
    "bilateral_difference",
    "line_angle_difference_degrees",
    "line_inclination_degrees",
    "segment_proportions_percent",
]
