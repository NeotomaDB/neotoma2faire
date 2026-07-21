"""Tests for neotoma2faire.extract.samples_pivot."""

import pandas as pd
import pytest

from neotoma2faire.extract.samples_pivot import get_samples


@pytest.fixture
def long_df():
    """Minimal long-format DataFrame with two taxa and three samples."""
    return pd.DataFrame({
        'sampleid': [1, 1, 2, 2, 3, 3],
        'taxonid':  [10, 20, 10, 20, 10, 20],
        'value':    [5.0, 0.0, 3.0, 1.0, 7.0, 2.0],
    })


class TestGetSamples:
    def test_returns_dataframe(self, long_df):
        result = get_samples(long_df)
        assert isinstance(result, pd.DataFrame)

    def test_taxonid_is_first_column(self, long_df):
        result = get_samples(long_df)
        assert result.columns[0] == 'taxonid'

    def test_sample_columns_named_correctly(self, long_df):
        result = get_samples(long_df)
        sample_cols = [c for c in result.columns if c != 'taxonid']
        assert all(c.startswith('sample_') for c in sample_cols)

    def test_one_row_per_taxon(self, long_df):
        result = get_samples(long_df)
        assert len(result) == 2  # two unique taxa

    def test_one_column_per_sample(self, long_df):
        result = get_samples(long_df)
        sample_cols = [c for c in result.columns if c != 'taxonid']
        assert len(sample_cols) == 3  # three unique samples

    def test_values_correct(self, long_df):
        result = get_samples(long_df)
        row = result[result['taxonid'] == 10].iloc[0]
        assert row['sample_1'] == 5.0
        assert row['sample_2'] == 3.0
        assert row['sample_3'] == 7.0

    def test_repeated_rows_preserved_not_merged(self):
        """Identical (taxonid, sampleid, value) repeats are kept as separate rows."""
        df = pd.DataFrame({
            'sampleid': [1, 1],
            'taxonid':  [10, 10],
            'value':    [5.0, 5.0],
        })
        result = get_samples(df)
        assert len(result) == 2
        assert list(result['taxonid']) == [10, 10]
        assert list(result['sample_1']) == [5.0, 5.0]

    def test_repeated_taxon_rows_kept_not_summed(self):
        """Several ASVs mapped to one taxon in a sample stay as separate rows."""
        df = pd.DataFrame({
            'sampleid': [1, 1, 2],
            'taxonid':  [10, 10, 10],
            'value':    [5.0, 3.0, 4.0],
        })
        result = get_samples(df)
        assert len(result) == 2  # two occurrences for taxon 10 in sample 1
        assert set(result['taxonid']) == {10}
        assert sorted(result['sample_1'].dropna()) == [3.0, 5.0]  # not summed to 8.0

    def test_extra_columns_ignored(self, long_df):
        """Columns beyond sampleid/taxonid/value must not affect output."""
        long_df['extra'] = 'noise'
        result = get_samples(long_df)
        assert 'extra' not in result.columns
