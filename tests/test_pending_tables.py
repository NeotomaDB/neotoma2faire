"""Tests for the getters whose Neotoma tables do not exist yet.

``ndb.samplestorage``, ``aednalibraries``, ``aednaampdata``, ``aednastddata``
and ``aednaelowquant`` are not in production, so these getters have nothing to
query.  What matters until they do is the *shape* of the placeholder: every
``write/*`` wrapper guards with ``if not df.empty``, so returning ``None``
would raise ``AttributeError`` the moment the corresponding ``add_*`` call is
uncommented in :mod:`~neotoma2faire.make_template`.
"""

import pandas as pd
import pytest

from neotoma2faire.extract.amp_data import get_amp_data
from neotoma2faire.extract.elow_quant import get_elow_quant
from neotoma2faire.extract.experiment_run import get_experiment_run
from neotoma2faire.extract.sample_storage import get_sample_storage
from neotoma2faire.extract.std_data import get_std_data

GETTERS = [
    get_sample_storage,
    get_experiment_run,
    get_amp_data,
    get_std_data,
    get_elow_quant,
]


@pytest.mark.parametrize("getter", GETTERS, ids=lambda f: f.__name__)
class TestPendingTableGetters:
    def test_returns_an_empty_dataframe_not_none(self, getter):
        result = getter(74666)
        assert isinstance(result, pd.DataFrame)
        assert result.empty

    def test_the_empty_guard_downstream_code_uses_works(self, getter):
        # This is the assertion that actually protects add_sheet_from_dataset.
        assert getter(74666).empty is True
