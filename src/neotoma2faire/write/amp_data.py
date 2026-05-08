"""Populate the ampData sheet with targeted amplification / qPCR data.

Thin wrapper around :func:`~.utils.add_sheet_from_dataset` that supplies the
``ampData`` sheet name and :func:`~.get_amp_data.get_amp_data` as the getter.

FAIRe ``ampData`` is intended for targeted qPCR assays where each row captures
one library × taxon detection event with Ct/Cq value, estimated copy number,
and a detection call (positive / negative / inconclusive).  This sheet is left
empty by the current pipeline because no equivalent data structure exists in
the production Neotoma schema.
"""

import pandas as pd

from ..extract.amp_data import get_amp_data
from ..utils import add_sheet_from_dataset


def add_amp_data(wb, dataset_id: int, header_row: int = 3) -> pd.DataFrame:
    """Fetch amplification data and write it to the ampData sheet.

    Args:
        wb (openpyxl.Workbook): Target workbook containing an ``ampData``
            sheet.
        dataset_id (int): Neotoma dataset ID.
        header_row (int): 1-based row index of the column-name header.
            Defaults to ``3``.

    Returns:
        pandas.DataFrame: The amplification data written to the sheet, or an
        empty DataFrame if no records exist in the imagined tables.
    """
    return add_sheet_from_dataset(wb, "ampData", get_amp_data, dataset_id, header_row)
