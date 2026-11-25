from app.completion import analysis_completion_issue, is_analysis_complete


def complete_panorama_values():
    from app.panoramic_form import PANORAMIC_PHASES
    phases = {}
    for index, phase in enumerate(PANORAMIC_PHASES, 1):
        answers = {
            label: options[0]
            for _, label, kind, options in phase["fields"]
            if kind == "choice" and options
        }
        phases[f"{index:02d}"] = {"Apartado": phase["title"], "Respuestas": answers}
    return {"Fases": phases}


def test_panorama_cannot_be_complete_without_required_phase_answers():
    issue = analysis_completion_issue("panoramic_systematic", {"Fases": {}})
    assert issue and "Panorámica" in issue


def test_panorama_rejects_a_partially_filled_repeater_row():
    from app.panoramic_form import PANORAMIC_PHASES
    values = complete_panorama_values()
    for index, phase in enumerate(PANORAMIC_PHASES, 1):
        for _, label, kind, options in phase["fields"]:
            if kind == "repeater":
                first_field = options[0][1]
                values["Fases"][f"{index:02d}"]["Respuestas"][label] = [{first_field: "Registro parcial"}]
                issue = analysis_completion_issue("panoramic_systematic", values)
                assert issue and "registro" in issue.lower()
                return
    raise AssertionError("The panoramic schema should contain a repeater field.")


def test_complete_panorama_requires_each_choice_but_accepts_no_evaluable_options():
    values = complete_panorama_values()
    assert analysis_completion_issue("panoramic_systematic", values) is None


def test_photo_analysis_requires_all_defined_landmarks():
    from app.photo_analysis import CONFIG
    key = "facial_frontal"
    points = {code: [index, index] for index, (code, _) in enumerate(CONFIG[key]["points"])}
    assert analysis_completion_issue(key, {"Puntos": points}) is None
    points.pop(next(iter(points)))
    assert "Faltan puntos" in analysis_completion_issue(key, {"Puntos": points})


def test_photo_visual_criteria_must_be_evaluated():
    from app.photo_analysis import CONFIG, SMILE_FIELDS
    points = {code: [index, index] for index, (code, _) in enumerate(CONFIG["smile"]["points"])}
    visual = {label: options[0] for label, options in SMILE_FIELDS.items()}
    values = {"Puntos": points, "Evaluación visual": visual}
    assert analysis_completion_issue("smile", values) is None
    visual.pop(next(iter(visual)))
    assert "criterios visuales" in analysis_completion_issue("smile", values).lower()


def test_little_requires_six_points_and_a_calculated_index():
    from app.little import CONTACTS
    points = {code: [index, index] for index, (code, _) in enumerate(CONTACTS)}
    values = {"Puntos": points, "Indice de Little px relativos": 5.0}
    assert analysis_completion_issue("little_upper", values) is None
    values["Puntos"].pop("P6")
    assert analysis_completion_issue("little_upper", values)


def test_cervical_no_evaluable_is_an_explicit_completed_observation():
    assert analysis_completion_issue(
        "cervical_maturation", {"Estadio vertebral": "No evaluable"}
    ) is None
    assert analysis_completion_issue("cervical_maturation", {}) is not None


def test_saved_complete_status_is_not_enough_without_valid_values():
    assert not is_analysis_complete("panoramic_systematic", {"status": "Completo", "values": {}})
    assert is_analysis_complete(
        "panoramic_systematic",
        {"status": "Completo", "values": complete_panorama_values()},
    )
