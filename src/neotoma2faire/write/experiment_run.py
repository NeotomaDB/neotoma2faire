"""Populate the experimentRunMetadata sheet with available Neotoma fields.

FAIRe ``experimentRunMetadata`` captures per-library sequencing metadata. This
sheet's template columns are ``samp_name``, ``assay_name``, ``pcr_plate_id``,
``lib_id`` and ``seq_run_id``.

This module writes one row per sample:

* ``samp_name`` — from the sample name.
* ``assay_name`` — from the dataset's aeDNA assay (``ndb.aednaassays.assayname``)
  when available, otherwise the Neotoma dataset type.
* ``pcr_plate_id`` / ``lib_id`` / ``seq_run_id`` — from the assay's library
  (``ndb.aednalibraries``) when available.

Any column without a source value is left blank.
"""

import pandas as pd

from ..utils import sort_samples, write_sheet_rows


def add_experiment_run(wb, df: pd.DataFrame, assays: list[dict] | None = None, header_row: int = 3):
    """Write one row per sample to the experimentRunMetadata sheet.

    Deduplicates *df* on ``sampleid`` and writes ``samp_name`` plus the assay /
    library columns.  When *assays* is provided, ``assay_name`` comes from the
    first assay and the library identifiers from its first library; otherwise
    ``assay_name`` falls back to ``datasettype``.

    Args:
        wb (openpyxl.Workbook): Target workbook containing an
            ``experimentRunMetadata`` sheet.
        df (pandas.DataFrame): Long-format DataFrame from
            :func:`~.get_data.get_data`.
        assays (list[dict] | None): Assay records from
            :func:`~.api.client.get_assays_by_dataset`.  Defaults to ``None``.
        header_row (int): 1-based row index of the column-name header.
            Defaults to ``3``.

    Returns:
        openpyxl.Workbook: The same workbook with ``experimentRunMetadata``
        populated.
    """
    # minimumDepthInMeters is carried only so the rows can be ordered the same
    # way as every other sheet; it is dropped again before writing.
    wanted = ("sampleid", "samp_name", "datasettype", "minimumDepthInMeters")
    available_cols = [c for c in wanted if c in df.columns]
    samples = df[available_cols].drop_duplicates(subset=["sampleid"])
    # Ordered before the datasettype -> assay_name rename, while samp_name still
    # exists under that name.
    samples = sort_samples(samples)

    assay = assays[0] if assays else {}
    libraries = assay.get("libraries") or []
    library = libraries[0] if libraries else {}

    if assay.get("assayname"):
        samples["assay_name"] = assay["assayname"]
    elif "datasettype" in samples.columns:
        samples = samples.rename(columns={"datasettype": "assay_name"})

    for col, key in (("pcr_plate_id", "pcrplateid"), ("lib_id", "libid"), ("seq_run_id", "seqrunid")):
        if library.get(key) is not None:
            samples[col] = library[key]

    write_sheet_rows(
        wb["experimentRunMetadata"],
        samples.drop(
            columns=["sampleid", "datasettype", "minimumDepthInMeters"], errors="ignore"
        ),
        header_row,
    )
    return wb
