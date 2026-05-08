"""Populate the stdData sheet with PCR standard curve data.

Thin wrapper around :func:`~.utils.add_sheet_from_dataset` that supplies the
``stdData`` sheet name and :func:`~.get_std_data.get_std_data` as the getter.

FAIRe ``stdData`` captures the calibration standards used to convert Ct/Cq
readings into absolute copy-number estimates: input quantity, amplification
efficiency, and R² of the fitted curve.  This sheet is left empty by the
current pipeline because no equivalent data structure exists in the production
Neotoma schema.
"""

import pandas as pd

from ..extract.std_data import get_std_data
from ..utils import add_sheet_from_dataset


def add_std_data(wb, dataset_id: int, header_row: int = 3) -> pd.DataFrame:
    """Fetch PCR standard curve data and write it to the stdData sheet.

    Args:
        wb (openpyxl.Workbook): Target workbook containing a ``stdData`` sheet.
        dataset_id (int): Neotoma dataset ID.
        header_row (int): 1-based row index of the column-name header.
            Defaults to ``3``.

    Returns:
        pandas.DataFrame: The standard curve data written to the sheet, or an
        empty DataFrame if no records exist in the imagined tables.
    """
    return add_sheet_from_dataset(wb, "stdData", get_std_data, dataset_id, header_row)
