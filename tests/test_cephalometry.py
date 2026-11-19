import math

from app.cephalometry import (
    REFERENCES,
    angle_at,
    angle_between_lines,
    calculate_cephalometry,
    project_to_line,
)


def test_angle_at_returns_right_angle():
    assert angle_at((0, 0), (0, 1), (1, 1)) == 90.0


def test_acute_angle_between_lines():
    value = angle_between_lines((0, 0), (1, 0), (0, 0), (1, 1), acute=True)
    assert math.isclose(value, 45.0, abs_tol=1e-8)


def test_projection_is_perpendicular_to_sn_line():
    projected = project_to_line((5, 4), (0, 0), (10, 0))
    assert projected == (5.0, 0.0)


def test_study_calculates_all_angles_and_segments_when_points_are_present():
    # Synthetic geometry validates computation paths, not clinical anatomy.
    points = {
        "S": (0, 0), "N": (100, 0),
        "A": (120, 20), "B": (120, 18), "D": (115, 22),
        "Ar": (40, 40), "Go": (110, 50), "Gn": (150, 65), "Me": (145, 80),
        "Pog": (155, 70), "Co": (35, 45),
        "U1_apex": (135, 30), "U1_tip": (150, 55),
    }
    result = calculate_cephalometry(points, pixels_per_mm=2)
    keys = {row["key"] for row in result["rows"]}
    assert keys == {reference.key for reference in REFERENCES}
    assert set(result["values"]) == {
        "SNA", "SNB", "ANB", "SND", "ArGoMe", "GoGnSN", "ABGoGn", "U1SN", "SL", "SE"
    }
    assert "L" in result["calculated_points"]
    assert "E" in result["calculated_points"]


def test_linear_segments_remain_pending_without_calibration():
    points = {
        "S": (0, 0), "N": (100, 0), "Pog": (140, 20), "Co": (20, 15)
    }
    result = calculate_cephalometry(points, pixels_per_mm=None)
    values = result["values"]
    assert "SL" not in values
    assert "SE" not in values
    assert {row["key"]: row for row in result["rows"]}["SL"]["classification"] == "Pendiente"


def test_anb_is_difference_between_sna_and_snb():
    points = {"S": (0, 0), "N": (10, 0), "A": (15, 5), "B": (15, 3)}
    result = calculate_cephalometry(points)
    assert math.isclose(result["values"]["ANB"], result["values"]["SNA"] - result["values"]["SNB"])


def test_upper_incisor_sn_angle_uses_steiner_obtuse_convention():
    # A 76-degree line intersection is reported as the 104-degree supplementary angle.
    points = {
        "S": (0, 0), "N": (1, 0),
        "U1_apex": (0, 0), "U1_tip": (math.cos(math.radians(76)), math.sin(math.radians(76))),
    }
    result = calculate_cephalometry(points)
    assert math.isclose(result["values"]["U1SN"], 104.0, abs_tol=1e-8)
