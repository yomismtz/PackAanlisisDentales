"""Geometría y referencia del análisis cefalométrico simplificado de Steiner.

Las normas son las aprobadas para esta primera versión en el documento del
proyecto. Las coordenadas se expresan en píxeles de la imagen original.
"""
from dataclasses import dataclass
import math

LANDMARKS = {
    "S": "Sella",
    "N": "Nasion",
    "A": "Punto A",
    "B": "Punto B",
    "D": "Punto D",
    "Ar": "Articulare",
    "Go": "Gonion",
    "Gn": "Gnathion",
    "Me": "Menton",
    "Pog": "Pogonion",
    "Co": "Contorno posterior del cóndilo",
    "U1_tip": "Borde incisal del incisivo superior",
    "U1_apex": "Ápice radicular del incisivo superior",
}

TRACE_PAIRS = (
    ("S", "N"),
    ("N", "A"),
    ("N", "B"),
    ("N", "D"),
    ("Ar", "Go"),
    ("Go", "Me"),
    ("Go", "Gn"),
    ("A", "B"),
    ("U1_apex", "U1_tip"),
)

@dataclass(frozen=True)
class MeasureReference:
    key: str
    label: str
    normal: str
    minimum: float
    maximum: float
    unit: str
    low_interpretation: str
    normal_interpretation: str
    high_interpretation: str

REFERENCES = (
    MeasureReference("SNA", "SNA", "82° ± 2°", 80, 84, "°",
                     "Tendencia a retrusión maxilar.",
                     "Posición maxilar dentro del intervalo de referencia.",
                     "Tendencia a protrusión maxilar."),
    MeasureReference("SNB", "SNB", "80° ± 2°", 78, 82, "°",
                     "Tendencia a retrusión mandibular.",
                     "Posición mandibular dentro del intervalo de referencia.",
                     "Tendencia a protrusión mandibular."),
    MeasureReference("ANB", "ANB", "2° ± 1°", 1, 3, "°",
                     "Tendencia a relación esquelética Clase III.",
                     "Relación sagital esquelética Clase I según esta referencia.",
                     "Tendencia a relación esquelética Clase II."),
    MeasureReference("SND", "SND", "77° ± 2°", 75, 79, "°",
                     "Tendencia a retrogenismo de la sínfisis mandibular.",
                     "Posición de la sínfisis dentro del intervalo de referencia.",
                     "Tendencia a progenismo de la sínfisis mandibular."),
    MeasureReference("ArGoMe", "Ar-Go-Me · ángulo goniaco", "125° ± 2°", 123, 127, "°",
                     "Configuración goniaca más cerrada.",
                     "Ángulo goniaco dentro del intervalo de referencia.",
                     "Configuración goniaca más abierta."),
    MeasureReference("GoGnSN", "Go-Gn / SN", "32° ± 5°", 27, 37, "°",
                     "Tendencia a patrón horizontal o rotación anterior.",
                     "Tendencia a patrón mesofacial.",
                     "Tendencia a patrón vertical o rotación posterior."),
    MeasureReference("ABGoGn", "AB-Go-Gn", "74° ± 2°", 72, 76, "°",
                     "Tendencia a mordida abierta.",
                     "Relación vertical maxilomandibular dentro del intervalo.",
                     "Tendencia a mordida profunda."),
    MeasureReference("U1SN", "Incisivo superior / SN", "104° ± 2°", 102, 106, "°",
                     "Tendencia a retroinclinación del incisivo superior.",
                     "Inclinación del incisivo superior dentro del intervalo.",
                     "Tendencia a proinclinación del incisivo superior."),
    MeasureReference("SL", "Segmento SL", "51 mm ± 2 mm", 49, 53, "mm",
                     "Mandíbula corta o posición de Pogonion más retruida.",
                     "Posición de Pogonion dentro del intervalo de referencia.",
                     "Mandíbula larga o posición de Pogonion más adelantada."),
    MeasureReference("SE", "Segmento SE", "23 mm ± 2 mm", 21, 25, "mm",
                     "Cóndilo en posición más adelantada respecto a SN.",
                     "Posición condilar dentro del intervalo de referencia.",
                     "Cóndilo en posición más retrasada respecto a SN."),
)

def _point(points, key):
    value = points.get(key)
    if value is None or len(value) != 2:
        raise ValueError(f"Falta el punto {key}.")
    return float(value[0]), float(value[1])

def distance(p1, p2):
    return math.hypot(float(p2[0]) - float(p1[0]), float(p2[1]) - float(p1[1]))

def angle_at(p1, vertex, p2):
    """Smaller included angle, in degrees, at vertex."""
    ax, ay = float(p1[0]) - float(vertex[0]), float(p1[1]) - float(vertex[1])
    bx, by = float(p2[0]) - float(vertex[0]), float(p2[1]) - float(vertex[1])
    denominator = math.hypot(ax, ay) * math.hypot(bx, by)
    if denominator == 0:
        raise ValueError("No se puede calcular un ángulo con puntos coincidentes.")
    cosine = max(-1.0, min(1.0, (ax * bx + ay * by) / denominator))
    return math.degrees(math.acos(cosine))

def angle_between_lines(a1, a2, b1, b2, acute=False):
    """Angle between two lines. acute=True returns the acute/obtuse supplement."""
    va = (float(a2[0]) - float(a1[0]), float(a2[1]) - float(a1[1]))
    vb = (float(b2[0]) - float(b1[0]), float(b2[1]) - float(b1[1]))
    if math.hypot(*va) == 0 or math.hypot(*vb) == 0:
        raise ValueError("No se puede calcular un ángulo con líneas de longitud cero.")
    a = math.atan2(va[1], va[0])
    b = math.atan2(vb[1], vb[0])
    delta = abs(math.degrees((a - b + math.pi) % (2 * math.pi) - math.pi))
    return min(delta, 180.0 - delta) if acute else delta

def project_to_line(point, line_start, line_end):
    """Orthogonal projection of point onto the infinite line start–end."""
    px, py = float(point[0]), float(point[1])
    ax, ay = float(line_start[0]), float(line_start[1])
    bx, by = float(line_end[0]), float(line_end[1])
    dx, dy = bx - ax, by - ay
    length2 = dx * dx + dy * dy
    if length2 == 0:
        raise ValueError("No se puede proyectar sobre una línea de longitud cero.")
    t = ((px - ax) * dx + (py - ay) * dy) / length2
    return ax + t * dx, ay + t * dy

def classify(value, reference):
    if value < reference.minimum:
        return "Disminuido", reference.low_interpretation
    if value > reference.maximum:
        return "Aumentado", reference.high_interpretation
    return "Dentro de norma", reference.normal_interpretation

def calculate_cephalometry(points, pixels_per_mm=None):
    """Calculate the eight configured angles and SL/SE when enough points exist."""
    result_values = {}
    calculated_points = {}
    sna = snb = None

    try:
        s, n, a = _point(points, "S"), _point(points, "N"), _point(points, "A")
        sna = angle_at(s, n, a)
        result_values["SNA"] = sna
    except (ValueError, KeyError):
        pass

    try:
        s, n, b = _point(points, "S"), _point(points, "N"), _point(points, "B")
        snb = angle_at(s, n, b)
        result_values["SNB"] = snb
    except (ValueError, KeyError):
        pass

    if sna is not None and snb is not None:
        result_values["ANB"] = sna - snb

    calculations = {
        "SND": lambda: angle_at(_point(points, "S"), _point(points, "N"), _point(points, "D")),
        "ArGoMe": lambda: angle_at(_point(points, "Ar"), _point(points, "Go"), _point(points, "Me")),
        "GoGnSN": lambda: angle_between_lines(
            _point(points, "S"), _point(points, "N"),
            _point(points, "Go"), _point(points, "Gn"), acute=True
        ),
        "ABGoGn": lambda: angle_between_lines(
            _point(points, "A"), _point(points, "B"),
            _point(points, "Go"), _point(points, "Gn"), acute=True
        ),
        "U1SN": lambda: angle_between_lines(
            _point(points, "S"), _point(points, "N"),
            _point(points, "U1_apex"), _point(points, "U1_tip"), acute=False
        ),
    }
    for key, calculation in calculations.items():
        try:
            result_values[key] = calculation()
        except (ValueError, KeyError):
            pass

    try:
        s, n, pog = _point(points, "S"), _point(points, "N"), _point(points, "Pog")
        l_point = project_to_line(pog, s, n)
        calculated_points["L"] = l_point
        if pixels_per_mm and pixels_per_mm > 0:
            result_values["SL"] = distance(s, l_point) / float(pixels_per_mm)
    except (ValueError, KeyError):
        pass

    try:
        s, n, co = _point(points, "S"), _point(points, "N"), _point(points, "Co")
        e_point = project_to_line(co, s, n)
        calculated_points["E"] = e_point
        if pixels_per_mm and pixels_per_mm > 0:
            result_values["SE"] = distance(s, e_point) / float(pixels_per_mm)
    except (ValueError, KeyError):
        pass

    rows = []
    for reference in REFERENCES:
        value = result_values.get(reference.key)
        if value is None:
            classification, interpretation = "Pendiente", "Faltan puntos o calibración."
            display_value = ""
        else:
            classification, interpretation = classify(value, reference)
            display_value = f"{value:.2f} {reference.unit}"
        rows.append({
            "key": reference.key,
            "label": reference.label,
            "normal": reference.normal,
            "value": value,
            "display_value": display_value,
            "classification": classification,
            "interpretation": interpretation,
        })
    return {"rows": rows, "values": result_values, "calculated_points": calculated_points}
