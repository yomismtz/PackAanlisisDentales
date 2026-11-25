"""Puente de compatibilidad para la geometría fotográfica del núcleo AVIS.

La implementación vive en :mod:`avis_core.geometry`; este módulo conserva
las rutas de importación usadas por la interfaz de escritorio.
"""
from avis_core.geometry import (
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
