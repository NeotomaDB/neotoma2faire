"""Tests for neotoma2faire.extract.sample_storage."""

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from neotoma2faire.extract.sample_storage import get_sample_storage


def _make_mock_conn(rows):
    """Return a mock psycopg v3 connection whose cursor yields *rows*."""
    cur = MagicMock()
    cur.__enter__ = lambda s: s
    cur.__exit__ = MagicMock(return_value=False)
    cur.fetchall.return_value = rows
    conn = MagicMock()
    conn.cursor.return_value = cur
    return conn


_SAMPLE_ROW = {
    "sampleid": 1,
    "samp_category": "sample",
    "neg_cont_type": None,
    "samp_store_sol": "ethanol",
    "samp_store_loc": "freezer A",
    "samp_store_temp": -20.0,
    "samp_store_dur": "6 months",
    "dna_store_loc": "freezer B",
    "verbatimSRS": "WGS84",
}


class TestGetSampleStorage:
    def test_returns_dataframe(self):
        with patch("neotoma2faire.extract.sample_storage.run_dataset_query",
                   return_value=pd.DataFrame([_SAMPLE_ROW])):
            result = get_sample_storage(55582)
        assert isinstance(result, pd.DataFrame)

    def test_empty_when_no_rows(self):
        with patch("neotoma2faire.extract.sample_storage.run_dataset_query",
                   return_value=pd.DataFrame()):
            result = get_sample_storage(55582)
        assert result.empty

    def test_has_sampleid_column(self):
        with patch("neotoma2faire.extract.sample_storage.run_dataset_query",
                   return_value=pd.DataFrame([_SAMPLE_ROW])):
            result = get_sample_storage(55582)
        assert "sampleid" in result.columns

    def test_has_samp_category_column(self):
        with patch("neotoma2faire.extract.sample_storage.run_dataset_query",
                   return_value=pd.DataFrame([_SAMPLE_ROW])):
            result = get_sample_storage(55582)
        assert "samp_category" in result.columns

    def test_has_storage_columns(self):
        with patch("neotoma2faire.extract.sample_storage.run_dataset_query",
                   return_value=pd.DataFrame([_SAMPLE_ROW])):
            result = get_sample_storage(55582)
        for col in ("samp_store_sol", "samp_store_loc", "samp_store_temp",
                    "samp_store_dur", "dna_store_loc", "verbatimSRS"):
            assert col in result.columns

    def test_multiple_rows(self):
        rows = [dict(_SAMPLE_ROW, sampleid=i) for i in range(1, 4)]
        with patch("neotoma2faire.extract.sample_storage.run_dataset_query",
                   return_value=pd.DataFrame(rows)):
            result = get_sample_storage(55582)
        assert len(result) == 3
