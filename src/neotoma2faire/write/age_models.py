"""Populate the ``ageModels`` sheet — the core's age-depth table.

Not a FAIRe checklist sheet, so it is created rather than filled in; see
:func:`~.extract.age_models.get_age_models` for where the columns come from.
"""

import pandas as pd

from ..extract.age_models import get_age_models
from ..utils import write_flat_sheet


def add_age_models(wb, df: pd.DataFrame) -> pd.DataFrame:
    """Write one age-depth row per sample to the ``ageModels`` sheet.

    Args:
        wb (openpyxl.Workbook): Target workbook.
        df (pandas.DataFrame): Long-format frame from
            :func:`~.extract.data.get_data`.

    Returns:
        pandas.DataFrame: The table written (empty when the dataset has no
        samples, in which case no sheet is created).
    """
    ages = get_age_models(df)
    write_flat_sheet(wb, "ageModels", ages, after="taxaFinal")
    return ages
