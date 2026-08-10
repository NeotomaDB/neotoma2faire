"""Populate the taxaFinal and taxaRaw sheets with one row per taxon.

This is a deliberately *flat* writer: it does **not** walk the taxonomic
hierarchy and does **not** query any imagined database tables.  Each row
contains just the taxon's identity (``scientificName``, ``taxonID``,
``taxonID_db``, ``verbatimIdentification``); the FAIRe rank columns
(``kingdom`` … ``specificEpithet``) and sequence columns (``seq_id``,
``dna_sequence``, etc.) are left blank because Neotoma's REST API does not
yet expose those fields.

Why not :func:`~.extract.taxa.get_taxa` / ``climb_up`` here?
    The hierarchy walk recursively follows ``highertaxonid`` links, which
    issues many small REST calls per taxon.  Until Neotoma's API exposes a
    "give me the full ancestry of these IDs" endpoint, the simpler "just
    paste the leaf names" approach is faster, more predictable, and free of
    DB-extension assumptions.
"""

import pandas as pd

from ..api.client import get_taxa_batch
from ..extract.taxa_sequences import get_taxa_sequences
from ..utils import write_sheet_rows


def add_taxa(
    wb,
    txid: int | list[int],
    header_row: int = 3,
    dataset_id: int | None = None,
) -> pd.DataFrame:
    """Fetch leaf taxa via the Neotoma REST API and write them to both sheets.

    Args:
        wb (openpyxl.Workbook): Target workbook containing ``taxaFinal`` and
            ``taxaRaw`` sheets.
        txid (int | list[int]): One or more Neotoma taxon IDs.
        header_row (int): 1-based row index of the column-name header in both
            taxa sheets.  Defaults to ``3``.
        dataset_id (int | None): When supplied, the dataset's DNA sequences are
            fetched via :func:`~.extract.taxa_sequences.get_taxa_sequences` and
            merged in, filling ``dna_sequence`` and ``seq_id``.  A taxon with
            several sequences yields one row per sequence, because the sequence
            — not the name — is what makes the row identifiable.  When ``None``,
            or when the dataset has no sequences on record, the frame is
            unchanged and those columns stay blank.

    Returns:
        pandas.DataFrame: One row per unique taxon ID (or per taxon × sequence
        when *dataset_id* supplies sequences) with columns ``scientificName``,
        ``taxonID``, ``taxonID_db``, ``verbatimIdentification``, optionally
        ``dna_sequence`` and ``seq_id``, plus the duplicate ``most_specific_id``
        / ``most_specific_name`` aliases used by the OTU merge in
        :func:`~.make_template.make_template`.
    """
    if isinstance(txid, int):
        txid = [txid]
    unique_ids = list({int(t) for t in txid})
    taxa = get_taxa_batch(unique_ids)

    df = pd.DataFrame(
        {
            "scientificName":         [t.get("taxonname") for t in taxa],
            "taxonID":                [t.get("taxonid")   for t in taxa],
            "taxonID_db":             "Neotoma",
            "verbatimIdentification": [t.get("taxonname") for t in taxa],
        }
    )
    # DNA sequences, when the caller names the dataset they belong to.
    # ndb.sequences carries no curation flag, so taxaRaw and taxaFinal still
    # receive the same rows.
    if dataset_id is not None:
        sequences = get_taxa_sequences(dataset_id)
        if not sequences.empty:
            sequences = sequences[["taxonid", "sequence", "sequenceid"]].rename(
                columns={
                    "taxonid": "taxonID",
                    "sequence": "dna_sequence",
                    "sequenceid": "seq_id",
                }
            )
            # The API returns IDs as strings in places; align both sides so the
            # merge matches instead of silently producing all-blank sequences.
            sequences["taxonID"] = pd.to_numeric(sequences["taxonID"], errors="coerce")
            df["taxonID"] = pd.to_numeric(df["taxonID"], errors="coerce")
            df = df.merge(sequences, on="taxonID", how="left")

    # Aliases consumed by make_template's OTU merge.  Keeping them here means
    # that pipeline keeps working without a hierarchy walk.
    df["most_specific_id"]   = df["taxonID"]
    df["most_specific_name"] = df["scientificName"]

    write_sheet_rows(wb["taxaFinal"], df, header_row)
    write_sheet_rows(wb["taxaRaw"],   df, header_row)
    return df
