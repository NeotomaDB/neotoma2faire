"""Tests for neotoma2faire.extract.taxa_sequences.

``get_taxa_sequences`` flattens the per-taxon ``sequences`` lists the API
returns into one row per (taxon × sequence). The sequence — not the taxon name
and not the ASV label — is the row key, because two taxa can share both.
"""

from unittest.mock import patch

from neotoma2faire.extract.taxa_sequences import SEQUENCE_COLUMNS, get_taxa_sequences


def _seq(sequenceid, sequence, asv="ASV1", model="DADA2"):
    return {
        "sequenceid": sequenceid,
        "sequence": sequence,
        "asv": asv,
        "model": model,
        "primername": "18SrRNAV7",
        "publicationdoi": "10.1000/example",
    }


def _run(payload):
    with patch(
        "neotoma2faire.extract.taxa_sequences.get_aedna_sequences", return_value=payload
    ):
        return get_taxa_sequences(74655)


class TestGetTaxaSequences:
    def test_no_records_yields_empty_frame_with_columns(self):
        df = _run([])

        assert df.empty
        assert list(df.columns) == SEQUENCE_COLUMNS

    def test_taxon_with_no_sequences_contributes_no_rows(self):
        assert _run([{"taxonid": 101, "taxonname": "Picea", "sequences": []}]).empty

    def test_missing_sequences_key_is_tolerated(self):
        assert _run([{"taxonid": 101, "taxonname": "Picea"}]).empty

    def test_null_sequences_is_tolerated(self):
        assert _run([{"taxonid": 101, "taxonname": "Picea", "sequences": None}]).empty

    def test_one_row_per_sequence(self):
        payload = [
            {
                "taxonid": 101,
                "taxonname": "Picea",
                "sequences": [_seq(1, "ACGT", "ASV1"), _seq(2, "TGCA", "ASV2")],
            }
        ]
        df = _run(payload)

        assert len(df) == 2
        assert list(df["sequence"]) == ["ACGT", "TGCA"]
        assert list(df["asv"]) == ["ASV1", "ASV2"]
        # Taxon identity repeats across that taxon's sequences.
        assert set(df["taxonid"]) == {101}
        assert set(df["taxonname"]) == {"Picea"}

    def test_columns_are_in_declared_order(self):
        payload = [{"taxonid": 101, "taxonname": "Picea", "sequences": [_seq(1, "ACGT")]}]

        assert list(_run(payload).columns) == SEQUENCE_COLUMNS

    def test_two_taxa_sharing_an_asv_stay_distinct_rows(self):
        """Same ASV label, different sequence — the sequence keeps them apart."""
        payload = [
            {"taxonid": 101, "taxonname": "Picea", "sequences": [_seq(1, "ACGT", "ASV1")]},
            {"taxonid": 202, "taxonname": "Abies", "sequences": [_seq(2, "TGCA", "ASV1")]},
        ]
        df = _run(payload)

        assert len(df) == 2
        assert set(df["asv"]) == {"ASV1"}
        assert list(df["sequence"]) == ["ACGT", "TGCA"]
        assert list(df["taxonid"]) == [101, 202]

    def test_absent_sequence_fields_become_none(self):
        payload = [{"taxonid": 101, "taxonname": "Picea", "sequences": [{"sequenceid": 1}]}]
        row = _run(payload).iloc[0]

        assert row["sequenceid"] == 1
        assert row["sequence"] is None
        assert row["asv"] is None
        assert row["model"] is None
