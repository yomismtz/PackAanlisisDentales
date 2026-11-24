from app.little import little_measurements

def test_little_sums_four_contact_displacements():
    points = {
        "C1": (0, 0),
        "C2": (3, 4),
        "C3": (6, 8),
        "C4": (9, 12),
        "C5": (12, 16),
    }
    segments, total = little_measurements(points)
    assert len(segments) == 4
    assert all(value == 5 for value in segments.values())
    assert total == 20

def test_little_does_not_report_total_with_missing_contact():
    points = {"C1": (0, 0), "C2": (3, 4), "C3": (6, 8)}
    segments, total = little_measurements(points)
    assert len(segments) == 2
    assert total is None

def test_little_returns_zero_for_coincident_contacts():
    points = {key: (10, 10) for key in ("C1", "C2", "C3", "C4", "C5")}
    segments, total = little_measurements(points)
    assert total == 0
