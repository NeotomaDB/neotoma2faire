"""neotoma2faire — Convert Neotoma datasets to the FAIRe checklist format.

Public API
----------
The following names are importable directly from ``neotoma2faire``:

* :func:`make_template` — orchestrate a full FAIRe template generation run.
* :func:`modify_README` — stamp the README sheet with version and timestamp.
* :func:`neo_connect` — open a psycopg connection to the Neotoma database.
* :func:`get_data` — download and merge a Neotoma dataset into a DataFrame.
* :func:`get_samples` — pivot long-format sample data to wide format.
* :func:`add_samples` — wrapper around :func:`get_samples` for workbook use.
* :func:`get_taxa` — build a taxonomic hierarchy DataFrame from taxon IDs.
* :func:`add_taxa` — wrapper around :func:`get_taxa` for workbook use.
"""

from .make_template import make_template
from .modify_README import modify_README
from .neo_connect import neo_connect
from .add_samples import add_samples
from .get_samples import get_samples
from .get_taxa import get_taxa
from .add_taxa import add_taxa
from .get_data import get_data
