from datetime import date
import pytest

from app.age_calculation import chronological_age, CERVICAL_STAGE_REFERENCE


def test_chronological_age_handles_birthday_and_month_boundaries():
    assert chronological_age(date(2012, 5, 24), date(2026, 11, 24)) == {
        "years": 14, "months": 6, "days": 0, "total_months": 174
    }
    assert chronological_age(date(2012, 10, 30), date(2026, 11, 24)) == {
        "years": 14, "months": 0, "days": 25, "total_months": 168
    }


def test_chronological_age_rejects_birth_after_study():
    with pytest.raises(ValueError):
        chronological_age("2027-01-01", "2026-11-24")


def test_cervical_reference_has_six_ordered_stages():
    assert list(CERVICAL_STAGE_REFERENCE) == [f"CS{i}" for i in range(1, 7)]
    assert CERVICAL_STAGE_REFERENCE["CS1"] < CERVICAL_STAGE_REFERENCE["CS6"]
