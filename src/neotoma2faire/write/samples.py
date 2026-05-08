"""Populate the sampleMetadata sheet and produce the OTU pivot.

:func:`add_samples` has two responsibilities:

1. **Write sampleMetadata** — calls :func:`~.get_sample_metadata.get_sample_metadata`
   to produce one row per sample and writes those rows into the
   ``sampleMetadata`` worksheet via :func:`~.utils.write_sheet_rows`.
   When the imagined ``ndb.samplestorage`` table is available, the optional
   *storage_df* (from :func:`~.get_sample_storage.get_sample_storage`) is
   merged in to supply FAIRe storage and sample-category fields that override
   the defaults derived from the Neotoma REST API.

2. **Return the OTU pivot** — calls :func:`~.get_samples.get_samples` to
   produce the wide taxa × samples matrix that will later be written to the
   standalone ``otuFinal`` CSV (FAIRe OTU tables are separate files, not
   sheets in the template workbook).
"""

import pandas as pd

from ..extract.sample_metadata import _AGE_COLS, _EXTRA_AGE_PREFIXES, get_sample_metadata
from ..extract.samples_pivot import get_samples
from ..utils import write_sheet_rows


def _append_age_columns(ws, df: pd.DataFrame, header_row: int) -> None:
    """Append age columns that are absent from the sheet header.

    Finds all age-related columns in *df* that do not already appear in
    *ws* row *header_row*, writes their names into the next available columns,
    then delegates data writing to :func:`~.utils.write_sheet_rows`.

    Args:
        ws: An openpyxl ``Worksheet`` (the ``sampleMetadata`` sheet).
        df (pandas.DataFrame): Per-sample metadata DataFrame.
        header_row (int): 1-based row index of the column-name header in *ws*.
    """
    existing = {cell.value for cell in ws[header_row] if cell.value is not None}
    extra = [
        c for c in df.columns
        if c not in existing and (c in _AGE_COLS or c.startswith(_EXTRA_AGE_PREFIXES))
    ]
    if not extra:
        return

    last_col = max(cell.column for cell in ws[header_row] if cell.value is not None)
    for offset, col_name in enumerate(extra, start=1):
        ws.cell(row=header_row, column=last_col + offset, value=col_name)

    write_sheet_rows(ws, df[extra], header_row)


def add_samples(
    wb,
    df: pd.DataFrame,
    storage_df: pd.DataFrame | None = None,
    header_row: int = 3,
) -> pd.DataFrame:
    """Write per-sample metadata to the workbook and return the OTU pivot.

    Calls :func:`~.get_sample_metadata.get_sample_metadata` to deduplicate
    *df* to one row per sample.  When *storage_df* is provided and non-empty,
    its columns (``samp_category``, ``neg_cont_type``, ``samp_store_sol``,
    etc.) are merged in on ``sampleid``, overriding any columns that were
    already present in the base metadata.  The merged result is then written
    to the ``sampleMetadata`` worksheet via :func:`~.utils.write_sheet_rows`.

    Args:
        wb (openpyxl.Workbook): Target workbook containing a ``sampleMetadata``
            sheet.
        df (pandas.DataFrame): Long-format DataFrame from
            :func:`~.get_data.get_data` (one row per sample × taxon).
        storage_df (pandas.DataFrame | None): Per-sample storage metadata from
            :func:`~.get_sample_storage.get_sample_storage`.  When ``None``
            or empty, only the base API-derived metadata is written.
            Defaults to ``None``.
        header_row (int): 1-based row index of the column-name header in the
            ``sampleMetadata`` sheet.  Defaults to ``3``.

    Returns:
        pandas.DataFrame: Wide-format OTU pivot with ``taxonid`` as the first
        column and one ``sample_<sampleid>`` column per unique sample.
    """
    meta = get_sample_metadata(df)

    if storage_df is not None and not storage_df.empty:
        # Storage columns take precedence: drop from meta any column that
        # storage_df will supply (except the join key).
        storage_cols = [c for c in storage_df.columns if c != "sampleid"]
        meta = meta.drop(columns=[c for c in storage_cols if c in meta.columns], errors="ignore")
        meta = meta.merge(storage_df, on="sampleid", how="left")

    write_sheet_rows(wb["sampleMetadata"], meta, header_row)
    _append_age_columns(wb["sampleMetadata"], meta, header_row)
    return get_samples(df)
