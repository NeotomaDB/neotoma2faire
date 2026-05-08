"""Populate the experimentRunMetadata sheet with available Neotoma fields.

FAIRe ``experimentRunMetadata`` captures per-library sequencing metadata
(library concentrations, index sequences, filenames, read counts, etc.).
Most of these fields require sequencing-pipeline provenance that is not
stored in Neotoma for legacy paleoecology records.

This module writes the subset of fields that *can* be derived from Neotoma:

* ``samp_name`` — from the sample name.
* ``assay_name`` — from the dataset type (e.g. ``"pollen surface sample"``).

All other columns are left blank.
"""

import pandas as pd

from ..utils import write_sheet_rows


def add_experiment_run(wb, df: pd.DataFrame, header_row: int = 3):
    """Write one row per sample to the experimentRunMetadata sheet.

    Deduplicates *df* on ``sampleid`` and writes ``samp_name`` and
    ``assay_name`` (mapped from ``datasettype``) for each unique sample.
    All sequencing-specific columns are left empty.

    Args:
        wb (openpyxl.Workbook): Target workbook containing an
            ``experimentRunMetadata`` sheet.
        df (pandas.DataFrame): Long-format DataFrame from
            :func:`~.get_data.get_data`.
        header_row (int): 1-based row index of the column-name header.
            Defaults to ``3``.

    Returns:
        openpyxl.Workbook: The same workbook with ``experimentRunMetadata``
        populated.
    """
    # Build one row per sample with only the columns we can populate
    available_cols = [c for c in ("sampleid", "samp_name", "datasettype") if c in df.columns]
    samples = df[available_cols].drop_duplicates(subset=["sampleid"]).reset_index(drop=True)

    # Rename datasettype → assay_name to match the FAIRe column name
    if "datasettype" in samples.columns:
        samples = samples.rename(columns={"datasettype": "assay_name"})

    # Drop the internal sampleid before writing (not a FAIRe column)
    write_sheet_rows(wb["experimentRunMetadata"], samples.drop(columns=["sampleid"], errors="ignore"), header_row)

    return wb
