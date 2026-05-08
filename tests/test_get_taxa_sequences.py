"""Tests for neotoma2faire.extract.taxa_sequences."""

from unittest.mock import patch

import pandas as pd
import pytest

from neotoma2faire.extract.taxa_sequences import get_taxa_sequences


_SEQ_ROW = {
    "seq_id": "ASV001",
    "asv_sequence": "ACGTACGT",
    "taxonid": 42,
    "pident": 98.5,
    "qcovs": 100.0,
    "reference_db": "PR2",
    "reference_sequence": "ASV001_ref",
    "is_curated": False,
    "lib_id": "LIB001",
    "sampleid": 1,
}


class TestGetTaxaSequences:
    def test_returns_dataframe(self):
        with patch("neotoma2faire.extract.taxa_sequences.run_dataset_query",
                   return_value=pd.DataFrame([_SEQ_ROW])):
            result = get_taxa_sequences(55582)
        assert isinstance(result, pd.DataFrame)

    def test_empty_when_no_rows(self):
        with patch("neotoma2faire.extract.taxa_sequences.run_dataset_query",
                   return_value=pd.DataFrame()):
            result = get_taxa_sequences(55582)
        assert result.empty

    def test_has_seq_id_column(self):
        with patch("neotoma2faire.extract.taxa_sequences.run_dataset_query",
                   return_value=pd.DataFrame([_SEQ_ROW])):
            result = get_taxa_sequences(55582)
        assert "seq_id" in result.columns

    def test_has_pident_and_qcovs(self):
        with patch("neotoma2faire.extract.taxa_sequences.run_dataset_query",
                   return_value=pd.DataFrame([_SEQ_ROW])):
            result = get_taxa_sequences(55582)
        assert "pident" in result.columns
        assert "qcovs" in result.columns

    def test_curated_false_by_default(self):
        """Calling with no curated argument should embed FALSE in the query."""
        captured = {}

        def fake_run(query, dataset_id):
            captured["query"] = query
            return pd.DataFrame()

        with patch("neotoma2faire.extract.taxa_sequences.run_dataset_query", side_effect=fake_run):
            get_taxa_sequences(55582)

        assert "FALSE" in captured["query"]
        assert "TRUE" not in captured["query"]

    def test_curated_true_passes_true(self):
        """Calling with curated=True should embed TRUE in the query."""
        captured = {}

        def fake_run(query, dataset_id):
            captured["query"] = query
            return pd.DataFrame()

        with patch("neotoma2faire.extract.taxa_sequences.run_dataset_query", side_effect=fake_run):
            get_taxa_sequences(55582, curated=True)

        assert "TRUE" in captured["query"]
        assert "FALSE" not in captured["query"]

    def test_multiple_rows(self):
        rows = [dict(_SEQ_ROW, seq_id=f"ASV00{i}") for i in range(1, 4)]
        with patch("neotoma2faire.extract.taxa_sequences.run_dataset_query",
                   return_value=pd.DataFrame(rows)):
            result = get_taxa_sequences(55582)
        assert len(result) == 3
