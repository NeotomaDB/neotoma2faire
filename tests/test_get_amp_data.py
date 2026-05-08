"""Tests for neotoma2faire.extract.amp_data."""

from unittest.mock import patch

import pandas as pd
import pytest

from neotoma2faire.extract.amp_data import get_amp_data


_AMP_ROW = {
    "lib_id": "LIB001",
    "sampleid": 1,
    "taxonid": 42,
    "ct_cq": 28.5,
    "copy_number": 1500.0,
    "detection_call": "positive",
}


class TestGetAmpData:
    def test_returns_dataframe(self):
        with patch("neotoma2faire.extract.amp_data.run_dataset_query",
                   return_value=pd.DataFrame([_AMP_ROW])):
            result = get_amp_data(55582)
        assert isinstance(result, pd.DataFrame)

    def test_empty_when_no_rows(self):
        with patch("neotoma2faire.extract.amp_data.run_dataset_query",
                   return_value=pd.DataFrame()):
            result = get_amp_data(55582)
        assert result.empty

    def test_has_ct_cq_column(self):
        with patch("neotoma2faire.extract.amp_data.run_dataset_query",
                   return_value=pd.DataFrame([_AMP_ROW])):
            result = get_amp_data(55582)
        assert "ct_cq" in result.columns

    def test_has_detection_call_column(self):
        with patch("neotoma2faire.extract.amp_data.run_dataset_query",
                   return_value=pd.DataFrame([_AMP_ROW])):
            result = get_amp_data(55582)
        assert "detection_call" in result.columns

    def test_has_copy_number_column(self):
        with patch("neotoma2faire.extract.amp_data.run_dataset_query",
                   return_value=pd.DataFrame([_AMP_ROW])):
            result = get_amp_data(55582)
        assert "copy_number" in result.columns

    def test_multiple_rows(self):
        rows = [dict(_AMP_ROW, taxonid=i) for i in range(1, 4)]
        with patch("neotoma2faire.extract.amp_data.run_dataset_query",
                   return_value=pd.DataFrame(rows)):
            result = get_amp_data(55582)
        assert len(result) == 3
