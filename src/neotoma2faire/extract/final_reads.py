"""Build the read-count matrix for the ``finalReads`` sheet.

``finalReads`` is the other non-FAIRe sheet the Okoboji workbook carries: one
row per sequenced taxon, with its DNA sequence and ASV label, followed by one
column per sample holding that taxon's read count.

Rows are keyed by (taxon × DNA sequence), not by name: two taxa can share a
name — and even an ASV label — while differing only by their sequence, so the
sequence is what makes a row identifiable.  Taxa with no sequence on record are
left out, which also drops Neotoma's non-biological datum rows (the
"Sedimentation rate" pseudo-taxon belongs to ``ageModels``, not here).

Known gap: the per-datum link to a specific sequence lives in
``ndb.sequencedata``, which no endpoint exposes yet.  Where a taxon has several
sequences, its repeated count rows are paired with them positionally, and any
sequence left without a matching repeat gets blank counts.
"""

import pandas as pd

from ..utils import sort_samples
from .samples_pivot import get_samples

#: Identity columns, in Okoboji's order, that precede the per-sample counts.
BASE_COLUMNS = [
    "scientificName",
    "DNAsequence",
    "ASV",
    "taxonID_db",
    "Units",
    "verbatimIdentification",
]

#: Authority that assigned the taxon IDs these names come from.
TAXON_ID_DB = "Neotoma"


def _sample_columns(df: pd.DataFrame) -> dict:
    """Map ``sample_<sampleid>`` pivot columns to sample names, in sheet order.

    Insertion order is the sheet's column order, so ordering the samples here
    is what puts the read-count columns in depth order — shallowest first,
    depthless samples last, ties by natural name order.
    """
    samples = sort_samples(df.drop_duplicates(subset=["sampleid"]))
    return {
        f"sample_{row.sampleid}": row.samp_name
        for row in samples.itertuples()
        if row.samp_name is not None
    }


def get_final_reads(df: pd.DataFrame, sequences: pd.DataFrame) -> pd.DataFrame:
    """Build the ``finalReads`` table.

    Args:
        df (pandas.DataFrame): Long-format frame from :func:`~.data.get_data`
            (one row per sample × datum).
        sequences (pandas.DataFrame): One row per (taxon × sequence), from
            :func:`~.taxa_sequences.get_taxa_sequences`.

    Returns:
        pandas.DataFrame: Columns ``scientificName``, ``DNAsequence``, ``ASV``,
        ``taxonID_db``, ``Units``, ``verbatimIdentification``, then one column
        per sample name.  Empty (headers only) when the dataset has no
        sequences on record.
    """
    if sequences.empty or df.empty:
        return pd.DataFrame(columns=BASE_COLUMNS)

    names = _sample_columns(df)

    # Pair the n-th repeat of a taxon's counts with its n-th sequence.
    counts = get_samples(df, keep_occurrence=True)
    seqs = sequences.copy()
    seqs["occurrence"] = seqs.groupby("taxonid").cumcount()

    merged = seqs.merge(counts, on=["taxonid", "occurrence"], how="left")

    # Units come from the taxon's own datum rows ("reads" for metabarcoding).
    units = (
        df.dropna(subset=["taxonid"])
        .drop_duplicates(subset=["taxonid"])
        .set_index("taxonid")["units"]
        if "units" in df.columns
        else pd.Series(dtype=object)
    )

    out = pd.DataFrame(
        {
            "scientificName": merged["taxonname"],
            "DNAsequence": merged["sequence"],
            "ASV": merged["asv"],
            "taxonID_db": TAXON_ID_DB,
            "Units": merged["taxonid"].map(units),
            # Not stored in Neotoma: the workbook's original, pre-harmonisation
            # name is lost once the taxon is matched to ndb.taxa.
            "verbatimIdentification": None,
        }
    )
    for pivot_column, sample_name in names.items():
        if pivot_column in merged.columns:
            out[sample_name] = merged[pivot_column].to_numpy()
    return out
