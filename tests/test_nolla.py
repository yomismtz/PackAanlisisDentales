import pytest

from app.nolla import (
    NOLLA_STAGES,
    NOLLA_TABLE,
    QUADRANT_TEETH,
    estimate_age,
    format_age,
    sum_stages,
)


def test_nolla_has_eleven_stages_and_four_quadrants():
    assert set(NOLLA_STAGES) == set(range(11))
    assert len(QUADRANT_TEETH) == 4
    assert all(len(teeth) == 7 for teeth in QUADRANT_TEETH.values())


def test_reference_table_has_same_age_rows_for_both_sexes():
    assert list(NOLLA_TABLE["Femenino"]) == list(range(3, 16))
    assert list(NOLLA_TABLE["Masculino"]) == list(range(3, 16))


def test_seven_stage_values_are_summed_and_zero_is_valid():
    assert sum_stages([10, 9, 8, 7, 6, 5, 0]) == 45


def test_sum_requires_exactly_seven_valid_stages():
    with pytest.raises(ValueError):
        sum_stages([1, 2, 3])
    with pytest.raises(ValueError):
        sum_stages([1, 2, 3, 4, 5, 6, None])
    with pytest.raises(ValueError):
        sum_stages([1, 2, 3, 4, 5, 6, 11])


def test_female_interpolation_matches_supplied_example():
    estimate = estimate_age(58, "Femenino")
    assert estimate is not None
    assert round(estimate.decimal_age, 2) == 9.82
    assert (estimate.years, estimate.months) == (9, 9)
    assert estimate.lower_age == 9
    assert estimate.upper_age == 10
    assert format_age(estimate) == "9 años y 9 meses"


def test_exact_reference_value_returns_exact_age():
    estimate = estimate_age(58.9, "Femenino")
    assert estimate is not None
    assert estimate.decimal_age == 10.0
    assert format_age(estimate) == "10 años"


def test_male_interpolation_uses_male_column():
    estimate = estimate_age(58, "Masculino")
    assert estimate is not None
    assert estimate.lower_age == 11
    assert estimate.upper_age == 12
    assert round(estimate.decimal_age, 2) == 11.23


def test_outside_reference_range_is_not_extrapolated():
    assert estimate_age(10, "Femenino") is None
    assert estimate_age(70, "Masculino") is None


def test_upper_and_lower_use_same_reference_column():
    # The function intentionally does not take a jaw argument:
    # one and the same sex-specific table applies to every quadrant.
    assert estimate_age(58, "Femenino") == estimate_age(58, "Femenino")
