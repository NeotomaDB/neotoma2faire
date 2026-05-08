"""Tests for neotoma2faire.write.samples._append_age_columns."""

import pandas as pd
import openpyxl
import pytest

from neotoma2faire.write.samples import _append_age_columns


def _make_ws(headers: list[str], header_row: int = 3) -> openpyxl.worksheet.worksheet.Worksheet:
    """Return a worksheet with *headers* written into *header_row*."""
    wb = openpyxl.Workbook()
    ws = wb.active
    for col_idx, name in enumerate(headers, start=1):
        ws.cell(row=header_row, column=col_idx, value=name)
    return ws


@pytest.fixture
def meta_default():
    """One-row-per-sample DataFrame with default-chronology age columns."""
    return pd.DataFrame({
        "samp_name": ["S1", "S2"],
        "age": [131.7, 500.0],
        "ageOldest": [150.0, 520.0],
        "ageYoungest": [110.0, 480.0],
        "ageUnit": ["Calibrated radiocarbon years BP", "Calibrated radiocarbon years BP"],
    })


@pytest.fixture
def meta_multi():
    """One-row-per-sample DataFrame with default + extra-chronology age columns."""
    return pd.DataFrame({
        "samp_name": ["S1", "S2"],
        "age": [131.7, 500.0],
        "ageOldest": [150.0, 520.0],
        "ageYoungest": [110.0, 480.0],
        "ageUnit": ["Calibrated radiocarbon years BP", "Calibrated radiocarbon years BP"],
        "age_Varve_model": [120.0, 490.0],
        "ageOldest_Varve_model": [135.0, 505.0],
        "ageYoungest_Varve_model": [105.0, 475.0],
        "ageUnit_Varve_model": ["Varve years BP", "Varve years BP"],
    })


class TestAppendAgeColumns:
    def test_age_headers_appended(self, meta_default):
        ws = _make_ws(["samp_name"])
        _append_age_columns(ws, meta_default, header_row=3)
        headers = [ws.cell(row=3, column=c).value for c in range(1, 6)]
        assert "age" in headers
        assert "ageOldest" in headers
        assert "ageYoungest" in headers
        assert "ageUnit" in headers

    def test_age_data_written(self, meta_default):
        ws = _make_ws(["samp_name"])
        _append_age_columns(ws, meta_default, header_row=3)
        headers = {ws.cell(row=3, column=c).value: c for c in range(1, 10) if ws.cell(row=3, column=c).value}
        assert ws.cell(row=4, column=headers["age"]).value == 131.7
        assert ws.cell(row=5, column=headers["age"]).value == 500.0

    def test_no_duplicate_headers(self, meta_default):
        """If age columns already exist in the sheet, they must not be added again."""
        ws = _make_ws(["samp_name", "age", "ageOldest", "ageYoungest", "ageUnit"])
        _append_age_columns(ws, meta_default, header_row=3)
        headers = [ws.cell(row=3, column=c).value for c in range(1, 10) if ws.cell(row=3, column=c).value]
        assert headers.count("age") == 1

    def test_extra_chron_headers_appended(self, meta_multi):
        ws = _make_ws(["samp_name"])
        _append_age_columns(ws, meta_multi, header_row=3)
        headers = {ws.cell(row=3, column=c).value for c in range(1, 15) if ws.cell(row=3, column=c).value}
        assert "age_Varve_model" in headers
        assert "ageUnit_Varve_model" in headers

    def test_no_age_columns_no_change(self):
        """When df has no age columns, the sheet header must be unchanged."""
        df = pd.DataFrame({"samp_name": ["S1"]})
        ws = _make_ws(["samp_name"])
        _append_age_columns(ws, df, header_row=3)
        headers = [ws.cell(row=3, column=c).value for c in range(1, 5)]
        assert headers == ["samp_name", None, None, None]
