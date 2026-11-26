from types import SimpleNamespace

from app.photo_analysis import PhotoAnalysisDialog


class FakeTable:
    def __init__(self):
        self.row_count = 0
        self.items = {}

    def setRowCount(self, count):
        self.row_count = count

    def clearContents(self):
        self.items.clear()

    def setItem(self, row, column, item):
        self.items[(row, column)] = item.text()

    def rows(self):
        return [
            tuple(self.items.get((row, column), "") for column in range(3))
            for row in range(self.row_count)
        ]


def make_dialog(formula, points, measures=()):
    def add_result(rows, label, value, reference=""):
        rows.append((label, value, reference))

    return SimpleNamespace(
        cfg={"formula": formula, "measures": list(measures)},
        points=points,
        results=FakeTable(),
        add_result=add_result,
        distance=lambda a, b: (
            ((points[b][0] - points[a][0]) ** 2 + (points[b][1] - points[a][1]) ** 2) ** 0.5
            if a in points and b in points else None
        ),
        vertical_distance=lambda a, b: (
            abs(points[b][1] - points[a][1]) if a in points and b in points else None
        ),
        horizontal_distance=lambda a, b: (
            abs(points[b][0] - points[a][0]) if a in points and b in points else None
        ),
    )


def test_smile_result_includes_angle_between_pupillary_and_commissural_lines():
    dialog = make_dialog(
        "smile",
        {
            "PUP_R": (0, 0), "PUP_L": (100, 0),
            "LC_R": (0, 20), "LC_L": (100, 30),
        },
    )
    PhotoAnalysisDialog.update_results(dialog)
    result = {row[0]: row[1] for row in dialog.results.rows()}
    assert "Diferencia angular bipupilar–comisural" in result
    assert result["Diferencia angular bipupilar–comisural"] == "5.71°"


def test_frontal_results_include_all_three_facial_third_percentages():
    points = {
        "Tr": (0, 0), "Of": (0, 20), "N": (0, 25),
        "Sn": (0, 50), "Me": (0, 100),
    }
    dialog = make_dialog("frontal", points)
    PhotoAnalysisDialog.update_results(dialog)
    result = {row[0]: row[1] for row in dialog.results.rows()}
    assert result["Tercio superior (%)"] == "20.0 %"
    assert result["Tercio medio (%)"] == "30.0 %"
    assert result["Tercio inferior (%)"] == "50.0 %"


def test_facial_level_inclination_is_normalized_for_endpoint_order():
    dialog = make_dialog(
        "levels",
        {"OD": (100, 10), "OI": (0, 0)},
        [("Nivel ocular", "OD", "OI")],
    )
    PhotoAnalysisDialog.update_results(dialog)
    result = {row[0]: row[1] for row in dialog.results.rows()}
    assert result["Nivel ocular"] == "+5.71°"
