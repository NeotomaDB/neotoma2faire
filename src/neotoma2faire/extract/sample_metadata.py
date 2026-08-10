"""Extract per-sample metadata from a get_data() DataFrame.

FAIRe's ``sampleMetadata`` sheet requires one row per sample, with each column
holding a metadata field.  :func:`get_data` returns one row per
(sample × taxon), so this module deduplicates on ``sampleid`` and keeps only
the columns that correspond to FAIRe ``sampleMetadata`` terms.

Chronology deliberately does not appear here: ages, age models and
sedimentation rates all live in the ``ageModels`` sheet
(:mod:`~.extract.age_models`), so a sample's identity and its dating stay in
separate tables.
"""

import pandas as pd

from ..utils import sort_samples

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
    # Internal context columns kept for traceability
    "siteid",
    "sitename",
    "collectionunitid",
    "datasetid",
    "datasettype",
]

def get_sample_metadata(df: pd.DataFrame) -> pd.DataFrame:
    """Produce one row per sample with FAIRe ``sampleMetadata`` column names.

    Takes the long-format output of :func:`~.get_data.get_data` (one row per
    sample × taxon) and collapses it to one row per unique ``sampleid``,
    keeping only the columns listed in ``_SAMPLE_COLS``.

    Columns that are not present in *df* are silently omitted from the result
    rather than raising an error, so the function degrades gracefully when
    optional fields are absent.

    Rows come back in the order every sheet uses: shallowest first, samples
    with no recorded depth last, ties broken by natural name order (see
    :func:`~.utils.sort_samples`).

    Args:
        df (pandas.DataFrame): Long-format DataFrame from
            :func:`~.get_data.get_data`.

    Returns:
        pandas.DataFrame: One row per unique ``sampleid``, containing only the
        FAIRe ``sampleMetadata`` columns that are available in *df*, ordered
        by depth then sample name.
    """
    available = [c for c in _SAMPLE_COLS if c in df.columns]
    samples = df[available].drop_duplicates(subset=["sampleid"])
    return sort_samples(samples)
