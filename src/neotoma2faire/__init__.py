"""neotoma2faire — Convert Neotoma datasets to the FAIRe checklist format.

Public API (importable directly from ``neotoma2faire``)
-------------------------------------------------------
* :func:`make_template` — orchestrate a full FAIRe template generation run.
* :func:`get_data` — download and merge a Neotoma dataset into a DataFrame.
* :func:`get_sample_metadata` — extract per-sample metadata.
* :func:`get_samples` — pivot long-format sample data to wide format (OTU matrix).
* :func:`get_taxa` — build a taxonomic hierarchy DataFrame from taxon IDs.
* :func:`add_samples` — write sampleMetadata sheet and return OTU pivot.
* :func:`add_taxa` — write taxaFinal/taxaRaw sheets and return hierarchy DataFrame.
* :func:`add_experiment_run` — write experimentRunMetadata sheet.
* :func:`modify_README` — stamp the README sheet with version and timestamp.
* :func:`neo_connect` — open a psycopg connection to the Neotoma database.

Subpackages
-----------
* :mod:`neotoma2faire.api` — REST and DB clients.
* :mod:`neotoma2faire.extract` — pull tidy DataFrames out of Neotoma.
* :mod:`neotoma2faire.write` — write DataFrames into the FAIRe workbook.
"""
from .extract.data import get_data
from .extract.sample_metadata import get_sample_metadata
from .extract.samples_pivot import get_samples
from .extract.taxa import get_taxa
from .make_template import make_template
from .write.experiment_run import add_experiment_run
from .write.project import add_project
from .write.readme import modify_README
from .write.samples import add_samples
from .write.taxa import add_taxa

__all__ = [
    "add_experiment_run",
    "add_project",
    "add_samples",
    "add_taxa",
    "get_data",
    "get_sample_metadata",
    "get_samples",
    "get_taxa",
    "make_template",
    "modify_README"
]
