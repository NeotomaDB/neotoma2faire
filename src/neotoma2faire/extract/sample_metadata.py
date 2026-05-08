"""Extract per-sample metadata from a get_data() DataFrame.

FAIRe's ``sampleMetadata`` sheet requires one row per sample, with each column
holding a metadata field.  :func:`get_data` returns one row per
(sample × taxon), so this module deduplicates on ``sampleid`` and keeps only
the columns that correspond to FAIRe ``sampleMetadata`` terms.
"""

import pandas as pd

# FAIRe sampleMetadata columns that can be populated from Neotoma via the API.
# Columns are listed in roughly the order they appear in the FAIRe template.
_SAMPLE_COLS = [
    "sampleid",           # internal key — used for deduplication
    "samp_name",          # FAIRe: samp_name
    "samp_category",      # FAIRe: samp_category  (hardcoded "sample")
    "decimalLatitude",    # FAIRe: decimalLatitude
    "decimalLongitude",   # FAIRe: decimalLongitude
    "elev",               # FAIRe: elev
    "geo_loc_name",       # FAIRe: geo_loc_name
    "eventDate",          # FAIRe: eventDate
    "verbatimEventDate",  # FAIRe: verbatimEventDate
    "minimumDepthInMeters",  # FAIRe: minimumDepthInMeters
    "maximumDepthInMeters",  # FAIRe: maximumDepthInMeters
    "materialSampleID",   # FAIRe: materialSampleID  (IGSN)
    "samp_collect_device",   # FAIRe: samp_collect_device
    "samp_collect_method",   # FAIRe: samp_collect_method
    "samp_mat_process",   # FAIRe: samp_mat_process
    "sample_derived_from",   # FAIRe: sample_derived_from  (analysisunitid)
    "env_medium",         # FAIRe: env_medium
    # Ages — default chronology maps to standard FAIRe columns
    "age",                # FAIRe: age
    "ageOldest",          # FAIRe: ageOldest
    "ageYoungest",        # FAIRe: ageYoungest
    "ageUnit",            # FAIRe: ageUnit  (e.g. "Calibrated radiocarbon years BP")
    # Internal context columns kept for traceability
    "siteid",
    "sitename",
    "collectionunitid",
    "datasetid",
    "datasettype",
]

# Standard FAIRe age column names (default chronology).
_AGE_COLS = {"age", "ageOldest", "ageYoungest", "ageUnit"}

# Prefixes used by get_data() for non-default chronology age columns.
_EXTRA_AGE_PREFIXES = ("age_", "ageOldest_", "ageYoungest_", "ageUnit_")


def get_sample_metadata(df: pd.DataFrame) -> pd.DataFrame:
    """Produce one row per sample with FAIRe ``sampleMetadata`` column names.

    Takes the long-format output of :func:`~.get_data.get_data` (one row per
    sample × taxon) and collapses it to one row per unique ``sampleid``,
    keeping only the columns listed in ``_SAMPLE_COLS``.

    Columns that are not present in *df* are silently omitted from the result
    rather than raising an error, so the function degrades gracefully when
    optional fields are absent.

    Args:
        df (pandas.DataFrame): Long-format DataFrame from
            :func:`~.get_data.get_data`.

    Returns:
        pandas.DataFrame: One row per unique ``sampleid``, containing only the
        FAIRe ``sampleMetadata`` columns that are available in *df*.
    """
    available = [c for c in _SAMPLE_COLS if c in df.columns]
    # Append columns for non-default chronologies in the order they appear in df.
    extra = [
        c for c in df.columns
        if c.startswith(_EXTRA_AGE_PREFIXES) and c not in available
    ]
    return df[available + extra].drop_duplicates(subset=["sampleid"]).reset_index(drop=True)
