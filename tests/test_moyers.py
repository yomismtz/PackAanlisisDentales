import pytest

from app.moyers import predict_moyers_75, moyers_discrepancy

def test_moyers_75_female_reference_values():
    assert predict_moyers_75(19.5, "Femenino", "superior") == 20.4
    assert predict_moyers_75(19.5, "Femenino", "inferior") == 19.6

def test_moyers_75_male_reference_values():
    assert predict_moyers_75(22.0, "Masculino", "superior") == 21.5
    assert predict_moyers_75(22.0, "Masculino", "inferior") == 21.5

def test_moyers_interpolates_between_table_rows():
    assert predict_moyers_75(20.25, "Femenino", "inferior") == 20.0

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
