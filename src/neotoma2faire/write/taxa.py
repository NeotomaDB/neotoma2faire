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
        dataset_id (int | None): Currently unused; kept in the signature for
            forward compatibility with a future hierarchy/sequence writer.

    Returns:
        pandas.DataFrame: One row per unique taxon ID with columns
        ``scientificName``, ``taxonID``, ``taxonID_db``,
        ``verbatimIdentification``, plus the duplicate ``most_specific_id`` /
        ``most_specific_name`` aliases used by the OTU merge in
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
    # Aliases consumed by make_template's OTU merge.  Keeping them here means
    # that pipeline keeps working without a hierarchy walk.
    df["most_specific_id"]   = df["taxonID"]
    df["most_specific_name"] = df["scientificName"]

    write_sheet_rows(wb["taxaFinal"], df, header_row)
    write_sheet_rows(wb["taxaRaw"],   df, header_row)
    return df
