"""Populate the ``finalReads`` sheet — read counts per sequenced taxon.

Not a FAIRe checklist sheet, so it is created rather than filled in.  The rows
are keyed by DNA sequence, not by taxon name; see
:func:`~.extract.final_reads.get_final_reads`.
"""

import pandas as pd

from ..extract.final_reads import get_final_reads
from ..extract.taxa_sequences import get_taxa_sequences
from ..utils import write_flat_sheet


def add_final_reads(wb, df: pd.DataFrame, dataset_id: int) -> pd.DataFrame:
    """Write one row per (taxon × DNA sequence) to the ``finalReads`` sheet.

    Args:
        wb (openpyxl.Workbook): Target workbook.
        df (pandas.DataFrame): Long-format frame from
            :func:`~.extract.data.get_data`.
        dataset_id (int): Neotoma dataset ID, used to fetch the sequences.

    Returns:
        pandas.DataFrame: The table written.  Empty for datasets with no
        sequences on record (every non-aeDNA dataset), in which case no sheet
        is created.
    """
    reads = get_final_reads(df, get_taxa_sequences(dataset_id))
    write_flat_sheet(wb, "finalReads", reads, after="ageModels")
    return reads
