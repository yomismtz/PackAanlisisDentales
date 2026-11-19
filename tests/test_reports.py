import pytest

from app.reports import (
    REPORT_MODULES,
    available_modules,
    build_report_snapshot,
    completed_keys,
)


def test_report_modules_match_the_requested_four_sections():
    assert tuple(REPORT_MODULES) == ("ceph", "pan", "models", "age")


def test_only_completed_analysis_is_available_in_a_module():
    data = {
        "panoramic_systematic": {"status": "Completo"},
        "levandoski": {"status": "En proceso"},
        "steiner": {"status": "Pendiente"},
    }
    assert completed_keys(data, "pan") == ("panoramic_systematic",)
    assert available_modules(data) == ("pan",)


def test_snapshot_includes_only_selected_completed_analysis_records():
    data = {
        "steiner": {"status": "Completo", "values": {"SNA": 82}},
        "panoramic_systematic": {"status": "Completo", "values": {"Calidad": "Adecuada"}},
        "levandoski": {"status": "En proceso", "values": {"SL": 53}},
        "dental_age": {"status": "Completo", "values": {"Nolla": 58}},
    }
    result = build_report_snapshot(data, ["ceph", "pan", "age"])
    assert set(result) == {"ceph", "pan", "age"}
    assert set(result["pan"]) == {"panoramic_systematic"}
    assert "levandoski" not in result["pan"]
    assert "models" not in result


def test_snapshot_rejects_empty_selection_or_incomplete_only_modules():
    with pytest.raises(ValueError):
        build_report_snapshot({}, [])
    with pytest.raises(ValueError):
        build_report_snapshot({"steiner": {"status": "En proceso"}}, ["ceph"])


def test_snapshot_rejects_unknown_module():
    with pytest.raises(ValueError):
        build_report_snapshot({"steiner": {"status": "Completo"}}, ["invalid"])
