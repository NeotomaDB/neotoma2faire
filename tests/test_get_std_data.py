"""Tests for neotoma2faire.extract.std_data."""

from unittest.mock import patch

import pandas as pd
import pytest

from neotoma2faire.extract.std_data import get_std_data


_STD_ROW = {
    "stddataid": 1,
    "assayid": 10,
    "target_gene": "18S rRNA",
    "subfragment": "V4",
    "input_quantity": 1000.0,
    "efficiency": 0.95,
    "r_squared": 0.998,
}


class TestGetStdData:
    def test_returns_dataframe(self):
        with patch("neotoma2faire.extract.std_data.run_dataset_query",
                   return_value=pd.DataFrame([_STD_ROW])):
            result = get_std_data(55582)
        assert isinstance(result, pd.DataFrame)

    def test_empty_when_no_rows(self):
        with patch("neotoma2faire.extract.std_data.run_dataset_query",
                   return_value=pd.DataFrame()):
            result = get_std_data(55582)
        assert result.empty

    def test_has_efficiency_column(self):
        with patch("neotoma2faire.extract.std_data.run_dataset_query",
                   return_value=pd.DataFrame([_STD_ROW])):
            result = get_std_data(55582)
        assert "efficiency" in result.columns

    def test_has_r_squared_column(self):
        with patch("neotoma2faire.extract.std_data.run_dataset_query",
                   return_value=pd.DataFrame([_STD_ROW])):
            result = get_std_data(55582)
        assert "r_squared" in result.columns

    def test_has_input_quantity_column(self):
        with patch("neotoma2faire.extract.std_data.run_dataset_query",
                   return_value=pd.DataFrame([_STD_ROW])):
            result = get_std_data(55582)
        assert "input_quantity" in result.columns
