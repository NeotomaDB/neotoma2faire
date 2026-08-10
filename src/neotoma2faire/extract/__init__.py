"""Pure functions that turn Neotoma API responses into tidy DataFrames.

Each module owns one sheet's worth of data.  All functions take a dataset ID
(or a pre-fetched DataFrame) and return a DataFrame.  None of these modules
touches an openpyxl Workbook.

The modules for the imagined tables (``amp_data``, ``elow_quant``,
``experiment_run``, ``sample_storage``, ``std_data``) stay commented out until
those tables are deployed.
"""

from .age_models import get_age_models
from .data import get_data
from .final_reads import get_final_reads
from .sample_metadata import get_sample_metadata
from .samples_pivot import get_samples
from .taxa import climb_up, get_taxa
from .taxa_sequences import get_taxa_sequences

__all__ = [
    "climb_up",
    "get_age_models",
    "get_data",
    "get_final_reads",
    "get_sample_metadata",
    "get_samples",
    "get_taxa",
    "get_taxa_sequences",
]
