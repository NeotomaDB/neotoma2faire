"""Tests for neotoma2faire.write.readme."""

from datetime import datetime
from unittest.mock import patch

import pytest
from openpyxl import Workbook

from neotoma2faire.write.readme import _VERSION, modify_README


@pytest.fixture
def workbook():
    wb = Workbook()
    wb.active.title = "README"
    return wb


class TestModifyREADME:
    def test_returns_workbook(self, workbook):
        assert modify_README(workbook) is workbook

    def test_writes_modified_by_below_the_version_slot(self, workbook):
        # A2 answers A1's "checklist version of;" prompt, so the tool stamp
        # goes on A3 rather than overwriting it.
        modify_README(workbook)
        assert workbook["README"]["A3"].value == f"Modified by: Neotoma2FAIRe v{_VERSION}"

    def test_writes_the_checklist_version_into_a2(self, workbook):
        modify_README(workbook, "1.0.2")
        assert workbook["README"]["A2"].value == "1.0.2"

    def test_without_a_version_a2_is_left_alone(self, workbook):
        modify_README(workbook)
        assert workbook["README"]["A2"].value is None

    def test_writes_generated_label(self, workbook):
        modify_README(workbook)
        assert workbook["README"]["A4"].value == "Date/Time generated:"

    def test_writes_generated_datetime(self, workbook):
        fixed = datetime(2026, 1, 1, 12, 0, 0)
        with patch("neotoma2faire.write.readme.datetime") as mock_dt:
            mock_dt.now.return_value = fixed
            modify_README(workbook)
        assert workbook["README"]["B4"].value == fixed
