"""Tests for neotoma2faire.write.project."""

import pytest
from openpyxl import Workbook

from neotoma2faire.write import project as project_mod
from neotoma2faire.write.project import add_project


@pytest.fixture
def project_workbook():
    """Workbook with a vertical projectMetadata sheet (term_name in col C)."""
    wb = Workbook()
    ws = wb.active
    ws.title = "projectMetadata"
    ws.cell(1, 1, "requirement_level_code")
    ws.cell(1, 3, "term_name")
    ws.cell(1, 4, "project_level")
    for r, term in enumerate(
        ["recordedBy", "project_contact", "project_id", "assay_name", "target_gene"],
        start=2,
    ):
        ws.cell(r, 3, term)
    return wb


def _term_value(ws, term):
    for r in range(2, ws.max_row + 1):
        if ws.cell(r, 3).value == term:
            return ws.cell(r, 4).value
    return None


class TestAddProject:
    def test_fills_terms_from_endpoint(self, project_workbook, monkeypatch):
        monkeypatch.setattr(project_mod, "get_projects_by_dataset", lambda _d: [{
            "projectname": "WOL_19",
            "participants": [
                {"contactname": "Trisha L. Spanbauer", "email": "trisha@uky.edu"},
                {"contactname": "Jane Doe", "email": "jane@uky.edu"},
            ],
        }])
        add_project(project_workbook, 3)
        ws = project_workbook["projectMetadata"]
        assert _term_value(ws, "project_id") == "WOL_19"
        assert _term_value(ws, "recordedBy") == "Trisha L. Spanbauer; Jane Doe"
        assert _term_value(ws, "project_contact") == "trisha@uky.edu; jane@uky.edu"

    def test_imagined_terms_stay_blank(self, project_workbook, monkeypatch):
        monkeypatch.setattr(project_mod, "get_projects_by_dataset", lambda _d: [{
            "projectname": "WOL_19", "participants": [],
        }])
        monkeypatch.setattr(project_mod, "get_dataset", lambda _d: {"datasets": []})
        add_project(project_workbook, 3)
        ws = project_workbook["projectMetadata"]
        assert _term_value(ws, "project_id") == "WOL_19"
        assert _term_value(ws, "assay_name") is None
        assert _term_value(ws, "target_gene") is None

    def test_project_without_participants_falls_back_to_pi(self, project_workbook, monkeypatch):
        monkeypatch.setattr(project_mod, "get_projects_by_dataset", lambda _d: [{
            "projectname": "WOL_19", "participants": [],
        }])
        monkeypatch.setattr(project_mod, "get_dataset", lambda _d: {
            "datasets": [{"datasetpi": [{"contactname": "Some PI"}]}],
        })
        add_project(project_workbook, 3)
        ws = project_workbook["projectMetadata"]
        assert _term_value(ws, "recordedBy") == "Some PI"
        assert _term_value(ws, "project_contact") is None

    def test_no_project_falls_back_to_pi(self, project_workbook, monkeypatch):
        monkeypatch.setattr(project_mod, "get_projects_by_dataset", lambda _d: [])
        monkeypatch.setattr(project_mod, "get_dataset", lambda _d: {
            "datasets": [{"datasetpi": [{"contactname": "Some PI"}]}],
        })
        add_project(project_workbook, 3)
        ws = project_workbook["projectMetadata"]
        assert _term_value(ws, "recordedBy") == "Some PI"
        assert _term_value(ws, "project_id") is None

    def test_returns_workbook(self, project_workbook, monkeypatch):
        monkeypatch.setattr(project_mod, "get_projects_by_dataset", lambda _d: [])
        monkeypatch.setattr(project_mod, "get_dataset", lambda _d: {"datasets": []})
        assert add_project(project_workbook, 3) is project_workbook
