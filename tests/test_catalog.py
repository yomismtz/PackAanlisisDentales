from app.catalog import (
    ANALYSES,
    ANALYSIS_REQUIREMENTS,
    SLOTS,
    UNAVAILABLE_ANALYSES,
    analyses_for_available_slots,
    analyses_for_slot,
)


def keys_for(slots):
    return {key for key, _ in analyses_for_available_slots(slots)}


def test_expected_views_and_history_slots_exist():
    expected = {
        "ceph_lateral", "panoramic", "extra_frontal", "extra_smiling",
        "extra_profile", "intra_right", "intra_left", "intra_frontal",
        "intra_upper", "intra_lower", "intra_extra", "model_upper_right",
        "model_lower_occlusal", "model_both_right", "model_both_left",
        "model_both_front", "carpal",
    }
    assert expected <= set(SLOTS)


def test_all_requirement_slots_exist_in_catalog():
    referenced = {
        slot
        for alternatives in ANALYSIS_REQUIREMENTS.values()
        for group in alternatives
        for slot in group
    }
    assert referenced <= set(SLOTS)


def test_steiner_and_cervical_maturation_require_lateral_cephalogram():
    assert keys_for({"ceph_lateral"}) >= {
        "steiner", "cranio_cervical", "cervical_maturation"
    }
    assert "steiner" not in keys_for({"panoramic"})


def test_panorama_exposes_only_panorama_compatible_analyses():
    available = keys_for({"panoramic"})
    assert {"panoramic_systematic", "levandoski", "dental_age"} <= available
    assert "steiner" not in available
    assert "cervical_maturation" not in available


def test_nolla_requires_panorama_and_not_carpal_or_intraoral_photographs():
    assert "dental_age" in keys_for({"panoramic"})
    assert "dental_age" not in keys_for({"carpal"})
    assert "dental_age" not in keys_for({"intra_frontal"})


def test_moyers_tanaka_and_nance_require_both_occlusal_model_views():
    assert not ({"moyers", "tanaka_johnston", "nance_carey"} & keys_for({"model_upper_occlusal"}))
    available = keys_for({"model_upper_occlusal", "model_lower_occlusal"})
    assert {"moyers", "tanaka_johnston", "nance_carey", "little_upper", "little_lower"} <= available
    assert "moyers" not in keys_for({"intra_right", "intra_left", "intra_frontal"})


def test_little_is_limited_to_its_corresponding_occlusal_model():
    assert "little_upper" in keys_for({"model_upper_occlusal"})
    assert "little_lower" not in keys_for({"model_upper_occlusal"})
    assert "little_lower" in keys_for({"model_lower_occlusal"})
    assert "little_upper" not in keys_for({"model_lower_occlusal"})


def test_intermaxillary_has_two_complete_alternative_study_sources():
    intraoral = {"intra_right", "intra_left", "intra_frontal"}
    occlusion_models = {"model_both_right", "model_both_left", "model_both_front"}
    assert "intermaxillary" not in keys_for({"intra_right", "intra_left"})
    assert "intermaxillary" in keys_for(intraoral)
    assert "intermaxillary" in keys_for(occlusion_models)


def test_baume_requires_complete_primary_dentition_views():
    assert "baume" not in keys_for({"intra_right", "intra_left"})
    assert "baume" in keys_for({"intra_right", "intra_left", "intra_frontal"})


def test_maturation_integration_requires_panorama_and_lateral_cephalogram():
    assert "maturation_integration" not in keys_for({"panoramic"})
    assert "maturation_integration" not in keys_for({"ceph_lateral"})
    assert "maturation_integration" in keys_for({"panoramic", "ceph_lateral"})


def test_facial_analyses_are_restricted_to_their_photo_type():
    frontal = keys_for({"extra_frontal"})
    smiling = keys_for({"extra_smiling"})
    profile = keys_for({"extra_profile"})
    assert {"facial_frontal", "facial_midlines", "facial_levels", "facial_contour", "facial_symmetry"} <= frontal
    assert smiling == {"smile"}
    assert {"facial_profile", "powell", "facial_projections"} <= profile


def test_unimplemented_palatal_height_is_not_offered_from_2d_photos_or_models():
    every_slot = set(SLOTS)
    assert "palatal_height" in UNAVAILABLE_ANALYSES
    assert "palatal_height" not in keys_for(every_slot)
    assert "palatal_height" not in {key for key, _ in analyses_for_slot("model_upper_occlusal")}


def test_every_listed_analysis_has_a_requirement_or_is_explicitly_unavailable():
    assert set(ANALYSES) == set(ANALYSIS_REQUIREMENTS) | UNAVAILABLE_ANALYSES


def test_slot_candidates_are_not_the_same_as_currently_available_analyses():
    # Una vista puede estar relacionada con Moyers, pero no basta por sí sola.
    assert "moyers" in {key for key, _ in analyses_for_slot("model_upper_occlusal")}
    assert "moyers" not in keys_for({"model_upper_occlusal"})
