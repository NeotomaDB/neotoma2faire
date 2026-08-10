"""Fetch the DNA sequences recorded for a dataset, one row per sequence.

``ndb.sequences`` and ``ndb.aednamodels`` are in production, and the REST API
exposes them at ``/v2.0/data/aedna/sequences/{datasetid}`` (grouped by taxon).
This module flattens that nested response into a tidy DataFrame — one row per
(taxon × sequence) — which is what the FAIRe ``finalReads`` sheet needs.

The sequence and its ASV label are what keep same-named taxa apart: two taxa
can share a name, and even an ASV label, while differing only by their DNA
sequence, so neither the name nor the ASV alone is a usable key.

Not yet available from the API: a per-datum link (``ndb.sequencedata``) tying
an individual read count to one specific sequence, and any curation flag that
would separate ``taxaRaw`` from ``taxaFinal``.
"""

import pandas as pd

from ..api.client import get_aedna_sequences

#: Columns of the returned DataFrame, in order.
SEQUENCE_COLUMNS = [
    "taxonid",
    "taxonname",
    "sequenceid",
    "sequence",
    "asv",
    "model",
    "primername",
    "publicationdoi",
]


def get_taxa_sequences(dataset_id: int) -> pd.DataFrame:
    """Return one row per (taxon × DNA sequence) for *dataset_id*.

    Calls :func:`~.api.client.get_aedna_sequences` and flattens the per-taxon
    ``sequences`` lists.  Datasets with no sequence records (every non-aeDNA
    dataset) yield an empty DataFrame, so callers can guard with
    :attr:`~pandas.DataFrame.empty`.

    Args:
        dataset_id (int): Neotoma dataset ID.

    Returns:
        pandas.DataFrame: Columns ``taxonid``, ``taxonname``, ``sequenceid``,
        ``sequence``, ``asv``, ``model``, ``primername``, ``publicationdoi``.
    """
    rows = []
    for taxon in get_aedna_sequences(dataset_id):
        for seq in taxon.get("sequences") or []:
            rows.append(
                {
                    "taxonid": taxon.get("taxonid"),
                    "taxonname": taxon.get("taxonname"),
                    "sequenceid": seq.get("sequenceid"),
                    "sequence": seq.get("sequence"),
                    "asv": seq.get("asv"),
                    "model": seq.get("model"),
                    "primername": seq.get("primername"),
                    "publicationdoi": seq.get("publicationdoi"),
                }
            )
    return pd.DataFrame(rows, columns=SEQUENCE_COLUMNS)
