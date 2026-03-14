"""Pytest configuration and shared fixtures for the neotoma2faire test suite.

rpy2 requires a working R installation, which is not available in CI
environments.  This module inserts lightweight ``MagicMock`` stubs for every
rpy2 sub-module into ``sys.modules`` *before* any test file imports the
package, so that the module-level R calls in ``get_data.py`` and
``get_taxa.py`` (e.g. ``importr('neotoma2')``, ``get_table(...)``) silently
return mock objects rather than raising ``ImportError`` or trying to start R.
"""

import sys
from unittest.mock import MagicMock

# ---------------------------------------------------------------------------
# Stub out rpy2 before anything else imports it
# ---------------------------------------------------------------------------
_rpy2_mocks = [
    "rpy2",
    "rpy2.robjects",
    "rpy2.robjects.packages",
    "rpy2.robjects.pandas2ri",
]
for _mod in _rpy2_mocks:
    sys.modules.setdefault(_mod, MagicMock())
