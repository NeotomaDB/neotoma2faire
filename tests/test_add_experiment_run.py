"""Tests for neotoma2faire.write.experiment_run."""

import pandas as pd
import pytest
from openpyxl import Workbook

from neotoma2faire.write.experiment_run import add_experiment_run


@pytest.fixture
def minimal_workbook():
    """Workbook with an experimentRunMetadata sheet that has a header row at row 3."""
    wb = Workbook()
    ws = wb.active
    ws.title = "experimentRunMetadata"
    # Row 3: column headers matching FAIRe experimentRunMetadata terms
    header_cols = ["samp_name", "assay_name", "pcr_plate_id", "lib_id", "seq_run_id"]
    for col_idx, name in enumerate(header_cols, start=1):
        ws.cell(row=3, column=col_idx, value=name)
    return wb


@pytest.fixture
def sample_df():
    """Minimal long-format DataFrame with two samples."""
    return pd.DataFrame({
        "sampleid":    [1, 1, 2, 2],
        "taxonid":     [10, 20, 10, 20],
        "value":       [5.0, 0.0, 3.0, 1.0],
        "samp_name":   ["Sample_1087", "Sample_1087", "Sample_1088", "Sample_1088"],
        "datasettype": ["pollen surface sample"] * 4,
    })


class TestAddExperimentRun:
    def test_returns_workbook(self, minimal_workbook, sample_df):
        result = add_experiment_run(minimal_workbook, sample_df)
        assert result is minimal_workbook

    def test_writes_one_row_per_sample(self, minimal_workbook, sample_df):
        add_experiment_run(minimal_workbook, sample_df)
        ws = minimal_workbook["experimentRunMetadata"]
        # Row 3 is header; data starts at row 4
        filled_rows = [
            r for r in ws.iter_rows(min_row=4, values_only=True)
            if any(v is not None for v in r)
        ]
        assert len(filled_rows) == 2

    def test_samp_name_written(self, minimal_workbook, sample_df):
        add_experiment_run(minimal_workbook, sample_df)
        ws = minimal_workbook["experimentRunMetadata"]
        # samp_name is column 1
        values = [ws.cell(row=r, column=1).value for r in (4, 5)]
        assert set(values) == {"Sample_1087", "Sample_1088"}

    def test_assay_name_written(self, minimal_workbook, sample_df):
        add_experiment_run(minimal_workbook, sample_df)
        ws = minimal_workbook["experimentRunMetadata"]
        # assay_name is column 2
        value = ws.cell(row=4, column=2).value
        assert value == "pollen surface sample"

    def test_no_samp_name_column_does_not_raise(self, minimal_workbook):
        """DataFrame without samp_name must not crash."""
        df = pd.DataFrame({
            "sampleid": [1],
            "taxonid": [10],
            "value": [5.0],
            "datasettype": ["pollen"],
        })
        add_experiment_run(minimal_workbook, df)  # should not raise

    def test_deduplication(self, minimal_workbook, sample_df):
        """Each sampleid must appear only once even if it has many taxa rows."""
        add_experiment_run(minimal_workbook, sample_df)
        ws = minimal_workbook["experimentRunMetadata"]
        filled_rows = [
            r for r in ws.iter_rows(min_row=4, values_only=True)
            if any(v is not None for v in r)
        ]
        assert len(filled_rows) == 2
