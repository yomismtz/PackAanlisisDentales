"""Contract tests for the UI-independent AVIS geometry core."""
import math

from avis_core.geometry import (
    bilateral_difference,
    line_angle_difference_degrees,
    line_inclination_degrees,
    segment_proportions_percent,
)


def test_core_geometry_exports_the_public_functions():
    assert callable(line_inclination_degrees)
    assert callable(line_angle_difference_degrees)
    assert callable(segment_proportions_percent)
    assert callable(bilateral_difference)


def test_core_line_inclination_is_endpoint_order_independent():
    forward = line_inclination_degrees((0, 0), (100, 10))
    reverse = line_inclination_degrees((100, 10), (0, 0))
    assert math.isclose(forward, reverse, abs_tol=1e-9)
    assert math.isclose(forward, math.degrees(math.atan2(10, 100)), abs_tol=1e-9)


def test_core_line_angle_difference_handles_parallel_perpendicular_and_degenerate():
    assert math.isclose(
        line_angle_difference_degrees((0, 0), (10, 0), (0, 5), (10, 5)),
        0.0,
        abs_tol=1e-9,
    )
    assert math.isclose(
        line_angle_difference_degrees((0, 0), (10, 0), (2, 0), (2, 10)),
        90.0,
        abs_tol=1e-9,
    )
    assert line_angle_difference_degrees((1, 1), (1, 1), (0, 0), (10, 0)) is None


def test_core_segment_proportions_are_percentages_of_total():
    values = segment_proportions_percent((20.0, 30.0, 50.0))
    assert values == (20.0, 30.0, 50.0)
    assert math.isclose(sum(values), 100.0, abs_tol=1e-9)
    assert segment_proportions_percent((0.0, 0.0)) is None
    assert segment_proportions_percent((2.0, -1.0)) is None


def test_core_bilateral_difference_reports_absolute_and_relative_values():
    difference, relative = bilateral_difference(12.0, 10.0)
    assert difference == 2.0
    assert math.isclose(relative, 2 / 11 * 100, abs_tol=1e-9)
    assert bilateral_difference(0.0, 0.0) == (0.0, None)
    assert bilateral_difference(10.0, None) is None
