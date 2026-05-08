"""Populate the eLowQuantData sheet with eLow Quant pipeline outputs.

Thin wrapper around :func:`~.utils.add_sheet_from_dataset` that supplies the
``eLowQuantData`` sheet name and :func:`~.get_elow_quant.get_elow_quant` as
the getter.

FAIRe ``eLowQuantData`` captures the per-library × taxon output of the eLow
Quant statistical pipeline, which is designed to evaluate detections in low
copy-number eDNA samples: a numeric score, a classification (low / medium /
high), and a confidence value.  This sheet is left empty by the current
pipeline because no equivalent data structure exists in the production Neotoma
schema.
"""

import pandas as pd

from ..extract.elow_quant import get_elow_quant
from ..utils import add_sheet_from_dataset


def add_elow_quant(wb, dataset_id: int, header_row: int = 3) -> pd.DataFrame:
    """Fetch eLow Quant scores and write them to the eLowQuantData sheet.

    Args:
        wb (openpyxl.Workbook): Target workbook containing an
            ``eLowQuantData`` sheet.
        dataset_id (int): Neotoma dataset ID.
        header_row (int): 1-based row index of the column-name header.
            Defaults to ``3``.

    Returns:
        pandas.DataFrame: The eLow Quant data written to the sheet, or an
        empty DataFrame if no records exist in the imagined tables.
    """
    return add_sheet_from_dataset(wb, "eLowQuantData", get_elow_quant, dataset_id, header_row)
