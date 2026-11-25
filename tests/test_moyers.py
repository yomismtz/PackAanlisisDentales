import pytest

from app.moyers import predict_moyers_75, moyers_discrepancy

def test_moyers_75_female_reference_values():
    assert predict_moyers_75(19.5, "Femenino", "superior") == 20.4
    assert predict_moyers_75(19.5, "Femenino", "inferior") == 19.6

def test_moyers_75_male_reference_values():
    assert predict_moyers_75(22.0, "Masculino", "superior") == 21.5
    assert predict_moyers_75(22.0, "Masculino", "inferior") == 21.5

def test_moyers_interpolates_between_table_rows():
    assert predict_moyers_75(20.25, "Femenino", "inferior") == 19.95

@pytest.mark.parametrize("value", [19.49, 25.51])
def test_moyers_rejects_values_outside_published_table(value):
    with pytest.raises(ValueError):
        predict_moyers_75(value, "Femenino", "inferior")

def test_moyers_discrepancy_interpretation():
    assert moyers_discrepancy(20,20) == (0, "Espacio exacto")
    value, label = moyers_discrepancy(22,20)
    assert value == 2 and "excedente" in label
    value, label = moyers_discrepancy(18,20)
    assert value == -2 and "déficit" in label


from app.mixed_dentition import (
    REFERENCE_TEETH,
    _incisor_sum_range,
    _available_range,
    _qualitative_result,
    tanaka_johnston,
)


def test_internal_reference_sizes_are_arch_specific():
    assert REFERENCE_TEETH["lower_lateral"]["mean"] == 6.1
    assert REFERENCE_TEETH["upper_lateral"]["mean"] == 7.1
    assert REFERENCE_TEETH["upper_central"]["mean"] == 8.8


def test_tanaka_johnston_predicts_per_hemiarch():
    assert tanaka_johnston(20.0, "superior") == 21.0
    assert tanaka_johnston(20.0, "inferior") == 20.5


def test_internal_incisor_rule_creates_an_uncertainty_range():
    widths = {"42": 60.0, "41": 54.0, "31": 54.0, "32": 62.0}
    estimated = _incisor_sum_range(widths)
    assert estimated is not None
    assert estimated[0] < estimated[1]
    assert estimated[0] > 0


def test_arch_reference_rule_creates_an_uncertainty_range():
    estimated = _available_range(220.0, 70.0, "upper_lateral")
    assert estimated is not None
    assert estimated[0] < estimated[1]
    assert estimated[0] > 0


def test_qualitative_result_only_commits_when_the_range_is_decisive():
    assert _qualitative_result((22, 23), (20, 21)) == "Hay espacio"
    assert _qualitative_result((18, 19), (20, 21)) == "No hay espacio"
    assert _qualitative_result((19, 22), (20, 21)) == "No concluyente"
