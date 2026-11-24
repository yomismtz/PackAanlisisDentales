from app.little import little_measurements

def test_little_sums_four_contact_displacements():
    points = {
        "P1": (0, 0),
        "P2": (3, 4),
        "P3": (6, 8),
        "P4": (9, 12),
        "P5": (12, 16),
        "P6": (15, 20),
    }
    segments, total = little_measurements(points)
    assert len(segments) == 5
    assert all(value == 5 for value in segments.values())
    assert total == 25

def test_little_does_not_report_total_with_missing_contact():
    points = {"P1": (0, 0), "P2": (3, 4), "P3": (6, 8)}
    segments, total = little_measurements(points)
    assert len(segments) == 2
    assert total is None

def test_little_returns_zero_for_coincident_contacts():
    points = {key: (10, 10) for key in ("P1", "P2", "P3", "P4", "P5", "P6")}
    segments, total = little_measurements(points)
    assert total == 0
