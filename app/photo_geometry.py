"""Geometría común para mediciones fotográficas relativas de AVIS."""
from __future__ import annotations

import math


def line_inclination_degrees(start: tuple[float, float], end: tuple[float, float]) -> float | None:
    """Inclinación respecto a la horizontal, independiente del sentido de la línea."""
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    if math.hypot(dx, dy) == 0:
        return None
    angle = math.degrees(math.atan2(dy, dx))
    return (angle + 90.0) % 180.0 - 90.0


def line_angle_difference_degrees(first_start, first_end, second_start, second_end):
    """Ángulo agudo entre dos líneas no orientadas, entre 0° y 90°."""
    first = line_inclination_degrees(first_start, first_end)
    second = line_inclination_degrees(second_start, second_end)
    if first is None or second is None:
        return None
    difference = abs(first - second)
    return min(difference, 180.0 - difference)


def segment_proportions_percent(lengths):
    """Distribución porcentual de segmentos respecto a su suma."""
    if not lengths or any(value < 0 for value in lengths):
        return None
    total = sum(lengths)
    if total <= 0:
        return None
    return tuple(value / total * 100.0 for value in lengths)


def bilateral_difference(right, left):
    """Diferencia absoluta y relativa porcentual entre dos longitudes bilaterales."""
    if right is None or left is None:
        return None
    difference = abs(right - left)
    mean = (right + left) / 2.0
    relative_percent = difference / mean * 100.0 if mean > 0 else None
    return difference, relative_percent
