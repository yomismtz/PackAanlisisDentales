"""Nolla dental-age reference table and interpolation helpers.

The reference table is the one supplied by the project owner. The same
seven-tooth table is used for any maxillary or mandibular quadrant; only the
sex-specific reference column changes.
"""
from dataclasses import dataclass

NOLLA_STAGES = {
    0: "Ausencia de cripta",
    1: "Presencia de cripta",
    2: "Calcificación inicial",
    3: "Un tercio de corona",
    4: "Dos tercios de corona",
    5: "Corona casi completa",
    6: "Corona completa",
    7: "Un tercio de raíz",
    8: "Dos tercios de raíz",
    9: "Raíz casi completa, ápice abierto",
    10: "Cierre apical completo",
}

# Sumas de estadios de siete dientes permanentes por cuadrante, sin tercer molar.
# Transcripción de la tabla aportada por la estudiante. Se aplica igual a
# maxilar y mandíbula; las columnas corresponden a sexo femenino y masculino.
NOLLA_TABLE = {
    "Femenino": {
        3: 19.0, 4: 19.7, 5: 26.1, 6: 31.7, 7: 39.5, 8: 47.2,
        9: 53.8, 10: 58.9, 11: 63.0, 12: 65.9, 13: 67.9, 14: 68.9, 15: 69.4,
    },
    "Masculino": {
        3: 15.0, 4: 15.5, 5: 19.4, 6: 24.4, 7: 30.2, 8: 37.2,
        9: 45.7, 10: 51.2, 11: 57.1, 12: 61.0, 13: 64.3, 14: 66.6, 15: 68.1,
    },
}

QUADRANT_TEETH = {
    "Superior derecho": ("17", "16", "15", "14", "13", "12", "11"),
    "Superior izquierdo": ("27", "26", "25", "24", "23", "22", "21"),
    "Inferior izquierdo": ("37", "36", "35", "34", "33", "32", "31"),
    "Inferior derecho": ("47", "46", "45", "44", "43", "42", "41"),
}


@dataclass(frozen=True)
class NollaAgeEstimate:
    decimal_age: float
    years: int
    months: int
    lower_age: int
    upper_age: int
    lower_score: float
    upper_score: float


def sum_stages(stages):
    """Return the sum of seven Nolla stages; empty values are not accepted."""
    values = list(stages)
    if len(values) != 7:
        raise ValueError("El análisis requiere exactamente siete dientes.")
    if any(value is None or value == "" for value in values):
        raise ValueError("Selecciona el estadio de los siete dientes.")
    parsed = []
    for value in values:
        number = int(value)
        if number not in NOLLA_STAGES:
            raise ValueError("Cada estadio debe estar entre 0 y 10.")
        parsed.append(number)
    return sum(parsed)


def estimate_age(score, sex):
    """Interpolate Nolla dental age from the supplied sex-specific table.

    Returns None outside the reference range. No extrapolation is performed.
    """
    if sex not in NOLLA_TABLE:
        raise ValueError("Selecciona femenino o masculino para usar la tabla.")
    value = float(score)
    table = NOLLA_TABLE[sex]
    ages = sorted(table)

    for age in ages:
        if abs(value - table[age]) < 1e-9:
            return NollaAgeEstimate(
                decimal_age=float(age), years=age, months=0,
                lower_age=age, upper_age=age,
                lower_score=table[age], upper_score=table[age],
            )

    if value < table[ages[0]] or value > table[ages[-1]]:
        return None

    for lower, upper in zip(ages, ages[1:]):
        low_score, high_score = table[lower], table[upper]
        if low_score < value < high_score:
            decimal_age = lower + ((value - low_score) / (high_score - low_score)) * (upper - lower)
            years = int(decimal_age)
            # The supplied teaching example converts the decimal fraction to
            # completed months (e.g. 9.82 years -> 9 years, 9 months).
            months = int((decimal_age - years) * 12 + 1e-9)
            return NollaAgeEstimate(
                decimal_age=decimal_age, years=years, months=months,
                lower_age=lower, upper_age=upper,
                lower_score=low_score, upper_score=high_score,
            )
    return None


def format_age(estimate):
    if estimate is None:
        return "No estimable con el rango de esta tabla."
    if estimate.months:
        return f"{estimate.years} años y {estimate.months} meses"
    return f"{estimate.years} años"
