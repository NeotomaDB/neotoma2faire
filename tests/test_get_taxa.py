"""Tests for neotoma2faire.get_taxa.

climb_up accepts an explicit ``taxa`` DataFrame so its tests bypass the
module-level R-loaded default entirely.

get_taxa calls climb_up internally without passing ``taxa=``, so the default
parameter (bound at function-definition time) cannot be patched via the
module attribute.  Instead we patch neotoma2faire.get_taxa.climb_up with a
thin wrapper that injects the test DataFrame as the ``taxa`` argument.
"""

import pandas as pd
import pytest
from neotoma2faire.get_taxa import climb_up, get_taxa
from unittest.mock import patch


# ---------------------------------------------------------------------------
# Shared test fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def taxa_df():
    """Small synthetic taxa table covering a three-level hierarchy.

    Hierarchy::

        1 (Kingdom)
        └── 2 (Phylum)
            └── 3 (Species)
    """
    return pd.DataFrame({
        'taxonid':       [1,    2,    3],
        'taxonname':     ['Kingdom', 'Phylum', 'Species'],
        'highertaxonid': [None,  1,    2],
    })


# ---------------------------------------------------------------------------
# climb_up
# ---------------------------------------------------------------------------

class TestClimbUp:
    def test_returns_list(self, taxa_df):
        result = climb_up(3, taxa=taxa_df)
        assert isinstance(result, list)

    def test_path_from_leaf_to_root(self, taxa_df):
        path = climb_up(3, taxa=taxa_df)
        names = [n['taxonname'] for n in path]
        assert names == ['Species', 'Phylum', 'Kingdom']

    def test_levels_start_at_one_and_increment(self, taxa_df):
        path = climb_up(3, taxa=taxa_df)
        assert [n['level'] for n in path] == [1, 2, 3]

    def test_path_from_root_has_single_node(self, taxa_df):
        path = climb_up(1, taxa=taxa_df)
        assert len(path) == 1
        assert path[0]['taxonname'] == 'Kingdom'

    def test_missing_start_id_returns_empty(self, taxa_df):
        path = climb_up(999, taxa=taxa_df)
        assert path == []

    def test_cycle_does_not_loop_forever(self):
        """A taxon that points to itself as parent must terminate."""
        df = pd.DataFrame({
            'taxonid':       [5],
            'taxonname':     ['Cyclic'],
            'highertaxonid': [5],
        })
        path = climb_up(5, taxa=df)
        assert len(path) == 1

    def test_node_ids_in_path(self, taxa_df):
        path = climb_up(3, taxa=taxa_df)
        assert [n['taxonid'] for n in path] == [3, 2, 1]


# ---------------------------------------------------------------------------
# get_taxa
# ---------------------------------------------------------------------------

def _climb_stub(taxa_df):
    """Return a climb_up replacement that always uses *taxa_df*."""
    def _inner(start_id, taxa=None):
        return climb_up(start_id, taxa=taxa_df)
    return _inner


class TestGetTaxa:
    def test_returns_dataframe(self, taxa_df):
        with patch('neotoma2faire.get_taxa.climb_up', _climb_stub(taxa_df)):
            result = get_taxa([3])
        assert isinstance(result, pd.DataFrame)

    def test_most_specific_name_populated(self, taxa_df):
        with patch('neotoma2faire.get_taxa.climb_up', _climb_stub(taxa_df)):
            result = get_taxa([3])
        assert result['most_specific_name'].iloc[0] == 'Species'

    def test_most_specific_id_populated(self, taxa_df):
        with patch('neotoma2faire.get_taxa.climb_up', _climb_stub(taxa_df)):
            result = get_taxa([3])
        assert result['most_specific_id'].iloc[0] == 3

    def test_no_id_columns_in_output(self, taxa_df):
        with patch('neotoma2faire.get_taxa.climb_up', _climb_stub(taxa_df)):
            result = get_taxa([3])
        id_cols = [c for c in result.columns if c.endswith('_id') and c != 'most_specific_id']
        assert id_cols == []

    def test_single_int_accepted(self, taxa_df):
        with patch('neotoma2faire.get_taxa.climb_up', _climb_stub(taxa_df)):
            result = get_taxa(3)
        assert len(result) == 1

    def test_deduplication_of_ids(self, taxa_df):
        """Passing the same ID twice must produce only one row."""
        with patch('neotoma2faire.get_taxa.climb_up', _climb_stub(taxa_df)):
            result = get_taxa([3, 3])
        assert len(result) == 1

    def test_multiple_ids(self, taxa_df):
        with patch('neotoma2faire.get_taxa.climb_up', _climb_stub(taxa_df)):
            result = get_taxa([1, 2, 3])
        assert len(result) == 3

    def test_level_columns_present(self, taxa_df):
        with patch('neotoma2faire.get_taxa.climb_up', _climb_stub(taxa_df)):
            result = get_taxa([3])
        level_cols = [c for c in result.columns if c.startswith('level_')]
        assert len(level_cols) >= 1
