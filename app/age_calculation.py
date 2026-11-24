"""Chronological age and cervical maturation reference helpers."""
from datetime import date

# Mean chronological ages associated with CS stages in the 2022 systematic
# review/meta-analysis of the Baccetti CVM method. These are population means,
# not individual bone-age predictions.
CERVICAL_STAGE_REFERENCE = {
    "CS1": 9.7, "CS2": 10.8, "CS3": 12.0,
    "CS4": 13.4, "CS5": 14.7, "CS6": 15.8,
}
CERVICAL_REFERENCE_NOTE = (
    "Medias poblacionales publicadas; varían según sexo, población y estudio. "
    "No deben interpretarse como edad ósea individual ni sustituir la valoración morfológica."
)

def chronological_age(birth_date, study_date=None):
    """Return completed years, months and days between two ISO dates."""
    if isinstance(birth_date, str):
        birth_date = date.fromisoformat(birth_date)
    study_date = study_date or date.today()
    if isinstance(study_date, str):
        study_date = date.fromisoformat(study_date)
    if birth_date > study_date:
        raise ValueError("La fecha de nacimiento no puede ser posterior al estudio.")
    years = study_date.year - birth_date.year
    months = study_date.month - birth_date.month
    days = study_date.day - birth_date.day
    if days < 0:
        from calendar import monthrange
        prev_month = study_date.month - 1 or 12
        prev_year = study_date.year if study_date.month > 1 else study_date.year - 1
        days += monthrange(prev_year, prev_month)[1]
        months -= 1
    if months < 0:
        months += 12
        years -= 1
    return {"years": years, "months": months, "days": days,
            "total_months": years * 12 + months}
