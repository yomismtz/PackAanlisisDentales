import math

from app.photo_geometry import (
    bilateral_difference,
    line_angle_difference_degrees,
    line_inclination_degrees,
    segment_proportions_percent,
)


def test_line_inclination_is_independent_of_endpoint_order():
    forward = line_inclination_degrees((0, 0), (100, 10))
    reverse = line_inclination_degrees((100, 10), (0, 0))
    assert math.isclose(forward, reverse, abs_tol=1e-9)
    assert math.isclose(forward, math.degrees(math.atan2(10, 100)), abs_tol=1e-9)


def test_angle_between_horizontal_and_sloped_lines_is_acute():
    value = line_angle_difference_degrees(
        (0, 0), (100, 0), (0, 0), (100, 10)
    )
    assert math.isclose(value, math.degrees(math.atan2(10, 100)), abs_tol=1e-9)


def test_angle_between_parallel_lines_is_zero_even_when_reversed():
    value = line_angle_difference_degrees(
        (0, 0), (100, 0), (100, 10), (0, 10)
    )
    assert math.isclose(value, 0.0, abs_tol=1e-9)


def test_perpendicular_lines_have_ninety_degree_difference():
    value = line_angle_difference_degrees(
        (0, 0), (100, 0), (5, 0), (5, 100)
    )
    assert math.isclose(value, 90.0, abs_tol=1e-9)


def test_degenerate_line_has_no_inclination_or_comparison():
    assert line_inclination_degrees((1, 1), (1, 1)) is None
    assert line_angle_difference_degrees(
        (1, 1), (1, 1), (0, 0), (10, 0)
    ) is None


def test_three_facial_thirds_are_percentages_of_their_combined_height():
    values = segment_proportions_percent((20.0, 30.0, 50.0))
    assert values == (20.0, 30.0, 50.0)
    assert math.isclose(sum(values), 100.0, abs_tol=1e-9)


def test_proportions_are_not_returned_for_zero_or_invalid_total():
    assert segment_proportions_percent((0.0, 0.0, 0.0)) is None
    assert segment_proportions_percent((10.0, -1.0)) is None


def test_bilateral_difference_reports_absolute_and_relative_values():
    difference, relative = bilateral_difference(12.0, 10.0)
    assert difference == 2.0
    assert math.isclose(relative, 2 / 11 * 100, abs_tol=1e-9)


def test_bilateral_difference_omits_relative_percent_when_mean_is_zero():
    assert bilateral_difference(0.0, 0.0) == (0.0, None)
    assert bilateral_difference(10.0, None) is None
