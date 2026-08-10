"""Tests for neotoma2faire.extract.sample_metadata."""

import pandas as pd
import pytest

from neotoma2faire.extract.sample_metadata import get_sample_metadata


@pytest.fixture
def long_df():
    """Minimal long-format DataFrame simulating get_data() output."""
    return pd.DataFrame({
        "sampleid":            [1, 1, 2, 2],
        "taxonid":             [10, 20, 10, 20],
        "value":               [5.0, 0.0, 3.0, 1.0],
        "samp_name":           ["S1", "S1", "S2", "S2"],
        "samp_category":       ["sample"] * 4,
        "decimalLatitude":     [43.15] * 4,
        "decimalLongitude":    [-91.28] * 4,
        "elev":                [333] * 4,
        "geo_loc_name":        ["United States, Iowa"] * 4,
        "eventDate":           [None] * 4,
        "verbatimEventDate":   [None] * 4,
        "minimumDepthInMeters": [0.0, 0.0, 1.0, 1.0],
        "maximumDepthInMeters": [0.0, 0.0, 1.0, 1.0],
        "materialSampleID":    [None] * 4,
        "samp_collect_device": [None] * 4,
        "samp_collect_method": [None] * 4,
        "samp_mat_process":    [None] * 4,
        "sample_derived_from": [852, 852, 853, 853],
        "env_medium":          ["Unknown"] * 4,
        "age":                 [131.7, 131.7, 500.0, 500.0],
        "ageOldest":           [150.0, 150.0, 520.0, 520.0],
        "ageYoungest":         [110.0, 110.0, 480.0, 480.0],
        "ageUnit":             ["Calibrated radiocarbon years BP"] * 4,
        "siteid":              [34] * 4,
        "sitename":            ["Linton"] * 4,
        "collectionunitid":    [34] * 4,
        "datasetid":           [34] * 4,
        "datasettype":         ["pollen surface sample"] * 4,
    })


@pytest.fixture
def long_df_multi_chron():
    """DataFrame simulating get_data() output with a second (non-default) chronology."""
    return pd.DataFrame({
        "sampleid":                     [1, 1, 2, 2],
        "taxonid":                      [10, 20, 10, 20],
        "value":                        [5.0, 0.0, 3.0, 1.0],
        "samp_name":                    ["S1", "S1", "S2", "S2"],
        "samp_category":                ["sample"] * 4,
        "decimalLatitude":              [43.15] * 4,
        "decimalLongitude":             [-91.28] * 4,
        "elev":                         [333] * 4,
        "geo_loc_name":                 ["United States, Iowa"] * 4,
        "eventDate":                    [None] * 4,
        "verbatimEventDate":            [None] * 4,
        "minimumDepthInMeters":         [0.0, 0.0, 1.0, 1.0],
        "maximumDepthInMeters":         [0.0, 0.0, 1.0, 1.0],
        "materialSampleID":             [None] * 4,
        "samp_collect_device":          [None] * 4,
        "samp_collect_method":          [None] * 4,
        "samp_mat_process":             [None] * 4,
        "sample_derived_from":          [852, 852, 853, 853],
        "env_medium":                   ["Unknown"] * 4,
        # Default chronology
        "age":                          [131.7, 131.7, 500.0, 500.0],
        "ageOldest":                    [150.0, 150.0, 520.0, 520.0],
        "ageYoungest":                  [110.0, 110.0, 480.0, 480.0],
        "ageUnit":                      ["Calibrated radiocarbon years BP"] * 4,
        # Non-default chronology (suffixed columns)
        "age_Varve_model":              [120.0, 120.0, 490.0, 490.0],
        "ageOldest_Varve_model":        [135.0, 135.0, 505.0, 505.0],
        "ageYoungest_Varve_model":      [105.0, 105.0, 475.0, 475.0],
        "ageUnit_Varve_model":          ["Varve years BP"] * 4,
        "siteid":                       [34] * 4,
        "sitename":                     ["Linton"] * 4,
        "collectionunitid":             [34] * 4,
        "datasetid":                    [34] * 4,
        "datasettype":                  ["pollen surface sample"] * 4,
    })


class TestGetSampleMetadata:
    def test_returns_dataframe(self, long_df):
        result = get_sample_metadata(long_df)
        assert isinstance(result, pd.DataFrame)

    def test_one_row_per_sample(self, long_df):
        result = get_sample_metadata(long_df)
        assert len(result) == 2  # two unique sampleids

    def test_no_taxon_column(self, long_df):
        result = get_sample_metadata(long_df)
        assert "taxonid" not in result.columns

    def test_no_value_column(self, long_df):
        result = get_sample_metadata(long_df)
        assert "value" not in result.columns

    def test_faire_columns_present(self, long_df):
        result = get_sample_metadata(long_df)
        for col in ("decimalLatitude", "decimalLongitude", "elev", "geo_loc_name",
                    "samp_name", "samp_category", "minimumDepthInMeters"):
            assert col in result.columns, f"Expected column '{col}' missing"

    def test_age_columns_excluded(self, long_df):
        """Chronology belongs to the ageModels sheet, not sampleMetadata."""
        result = get_sample_metadata(long_df)
        for col in ("age", "ageOldest", "ageYoungest", "ageUnit"):
            assert col not in result.columns, f"Age column '{col}' leaked into sampleMetadata"

    def test_values_correct(self, long_df):
        result = get_sample_metadata(long_df)
        row1 = result[result["sampleid"] == 1].iloc[0]
        assert row1["decimalLatitude"] == 43.15
        assert row1["samp_name"] == "S1"

    def test_multi_chron_extra_columns_excluded(self, long_df_multi_chron):
        """Non-default chronologies must not widen the sheet either."""
        result = get_sample_metadata(long_df_multi_chron)
        for col in ("age_Varve_model", "ageOldest_Varve_model",
                    "ageYoungest_Varve_model", "ageUnit_Varve_model"):
            assert col not in result.columns, f"Extra-chron column '{col}' leaked in"

    def test_multi_chron_sample_columns_still_present(self, long_df_multi_chron):
        result = get_sample_metadata(long_df_multi_chron)
        for col in ("samp_name", "decimalLatitude", "minimumDepthInMeters"):
            assert col in result.columns

    def test_missing_columns_silently_omitted(self):
        """Columns in _SAMPLE_COLS that are absent from df must not raise."""
        df = pd.DataFrame({
            "sampleid": [1],
            "taxonid": [10],
            "value": [5.0],
        })
        result = get_sample_metadata(df)
        assert len(result) == 1
        assert "sampleid" in result.columns

    def test_reset_index(self, long_df):
        result = get_sample_metadata(long_df)
        assert list(result.index) == list(range(len(result)))


class TestSampleOrdering:
    """sampleMetadata shares one ordering rule with the other sheets."""

    @pytest.fixture
    def scrambled_df(self):
        # Mirrors West Okoboji: the depthless sample arrives first, the rest
        # deepest-first, and WLO9 would sort after WLO10 lexicographically.
        return pd.DataFrame({
            "sampleid":             [1, 2, 3, 4],
            "samp_name":            ["WLO50", "WLO49", "WLO10", "WLO9"],
            "minimumDepthInMeters": [None, 32.5, 10.0, 9.0],
        })

    def test_rows_come_out_shallowest_first_with_depthless_last(self, scrambled_df):
        result = get_sample_metadata(scrambled_df)
        assert list(result["samp_name"]) == ["WLO9", "WLO10", "WLO49", "WLO50"]

    def test_index_is_reset_after_ordering(self, scrambled_df):
        assert list(get_sample_metadata(scrambled_df).index) == [0, 1, 2, 3]
