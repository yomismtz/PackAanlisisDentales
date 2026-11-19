from app.catalog import GROUPS, SLOTS, ANALYSES, analyses_for_slot

def test_expected_views_and_history_slots_exist():
    assert {"ceph_lateral","panoramic","extra_frontal","extra_smiling","extra_profile","intra_right","intra_left",
      "intra_frontal","intra_upper","intra_lower","intra_extra","model_upper_right","model_lower_occlusal",
      "model_both_right","model_both_left","model_both_front","carpal"} <= set(SLOTS)

def test_analysis_routing():
    assert "steiner" in [x[0] for x in analyses_for_slot("ceph_lateral")]
    assert "levandoski" in [x[0] for x in analyses_for_slot("panoramic")]
    assert "panoramic_systematic" in [x[0] for x in analyses_for_slot("panoramic")]
    assert "carpal" in [x[0] for x in analyses_for_slot("carpal")]

def test_age_analyses_use_the_expected_radiographs():
    assert "dental_age" in [x[0] for x in analyses_for_slot("panoramic")]
    assert "cervical_maturation" in [x[0] for x in analyses_for_slot("ceph_lateral")]

def test_smile_analysis_uses_smiling_extraoral_photo():
    assert "smile" in [x[0] for x in analyses_for_slot("extra_smiling")]
    assert "smile" not in [x[0] for x in analyses_for_slot("extra_frontal")]
