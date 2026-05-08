"""Tests for neotoma2faire.extract.elow_quant."""

from unittest.mock import patch

import pandas as pd
import pytest

from neotoma2faire.extract.elow_quant import get_elow_quant


_ELQ_ROW = {
    "lib_id": "LIB001",
    "sampleid": 1,
    "taxonid": 42,
    "elowquant_score": 0.72,
    "elowquant_class": "medium",
    "elowquant_conf": 0.88,
}


class TestGetElowQuant:
    def test_returns_dataframe(self):
        with patch("neotoma2faire.extract.elow_quant.run_dataset_query",
                   return_value=pd.DataFrame([_ELQ_ROW])):
            result = get_elow_quant(55582)
        assert isinstance(result, pd.DataFrame)

    def test_empty_when_no_rows(self):
        with patch("neotoma2faire.extract.elow_quant.run_dataset_query",
                   return_value=pd.DataFrame()):
            result = get_elow_quant(55582)
        assert result.empty

    def test_has_elowquant_score_column(self):
        with patch("neotoma2faire.extract.elow_quant.run_dataset_query",
                   return_value=pd.DataFrame([_ELQ_ROW])):
            result = get_elow_quant(55582)
        assert "elowquant_score" in result.columns

    def test_has_elowquant_class_column(self):
        with patch("neotoma2faire.extract.elow_quant.run_dataset_query",
                   return_value=pd.DataFrame([_ELQ_ROW])):
            result = get_elow_quant(55582)
        assert "elowquant_class" in result.columns

    def test_has_elowquant_conf_column(self):
        with patch("neotoma2faire.extract.elow_quant.run_dataset_query",
                   return_value=pd.DataFrame([_ELQ_ROW])):
            result = get_elow_quant(55582)
        assert "elowquant_conf" in result.columns

    def test_multiple_rows(self):
        rows = [dict(_ELQ_ROW, taxonid=i) for i in range(1, 4)]
        with patch("neotoma2faire.extract.elow_quant.run_dataset_query",
                   return_value=pd.DataFrame(rows)):
            result = get_elow_quant(55582)
        assert len(result) == 3
