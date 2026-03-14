"""Build taxonomic hierarchy tables from Neotoma taxa data.

The module loads the full Neotoma taxa table once at import time (via the
``neotoma2`` R package) and exposes two public helpers:

* :func:`climb_up` — walk the parent-child hierarchy upward from a single
  taxon ID and return the ordered path.
* :func:`get_taxa` — process a list of taxon IDs and return a DataFrame with
  one column per taxonomic level plus ``most_specific_name`` /
  ``most_specific_id`` convenience columns.
"""

from rpy2.robjects.packages import importr
import pandas as pd

from .utils import _r_to_df

neo2 = importr('neotoma2')

# Load the full taxa table once at module import time.
taxa_tbl = neo2.get_table('taxa', limit=65000)
taxa_df = _r_to_df(taxa_tbl)


def climb_up(start_id, taxa=taxa_df):
    """Walk the taxonomic hierarchy upward from *start_id*.

    Traverses the ``highertaxonid`` parent links in *taxa* starting at
    *start_id*, collecting each node until the root is reached, a cycle is
    detected, or a missing node is encountered.

    Args:
        start_id (int): Neotoma ``taxonid`` of the taxon to start from.
        taxa (pandas.DataFrame): DataFrame with at minimum the columns
            ``taxonid``, ``taxonname``, and ``highertaxonid``.  Defaults to
            the module-level ``taxa_df`` loaded at import time.

    Returns:
        list[dict]: Ordered list of nodes from *start_id* upward, where each
        node is a dict with keys ``level`` (int, starting at 1),
        ``taxonid`` (int), and ``taxonname`` (str).
    """
    taxa = taxa.set_index('taxonid').to_dict(orient='index')
    path = []
    visited = set()
    current = start_id
    level = 1
    while current is not None and current not in visited:
        visited.add(current)
        node = taxa.get(current)
        if not node:
            break
        path.append({
            "level": level,
            "taxonid": current,
            "taxonname": node["taxonname"]
        })
        parent = node["highertaxonid"]
        if parent is None or parent == current:
            break
        current = parent
        level += 1
    return path


def get_taxa(taxa_ids):
    """Build a hierarchical taxa DataFrame for a list of taxon IDs.

    For each ID in *taxa_ids*, :func:`climb_up` is called to retrieve the
    full ancestry path.  The results are assembled into a DataFrame where
    each column ``level_N`` holds the taxon name at depth *N* (1 = most
    specific, higher numbers = more general ancestors).  Two summary columns
    are added:

    * ``most_specific_name`` — name of the deepest non-null level.
    * ``most_specific_id`` — corresponding Neotoma taxon ID.

    The intermediate ``level_N_id`` columns are dropped before returning.

    Args:
        taxa_ids (int | list[int]): One or more Neotoma taxon IDs.

    Returns:
        pandas.DataFrame: One row per unique taxon ID, with columns
        ``level_1``, ``level_2``, …, ``most_specific_name``,
        ``most_specific_id``.
    """
    if isinstance(taxa_ids, int):
        taxa_ids = [taxa_ids]
    taxa_ids = list(set(taxa_ids))
    tx = pd.DataFrame()
    for taxon_id in taxa_ids:
        hierarchy = climb_up(taxon_id)
        path_sorted = sorted(hierarchy, key=lambda x: x["level"], reverse=True)
        taxon_names = [node["taxonname"] for node in path_sorted]
        taxon_ids_list = [node["taxonid"] for node in path_sorted]
        df = pd.DataFrame([taxon_names], columns=[f"level_{i+1}" for i in range(len(taxon_names))])
        for i, tid in enumerate(taxon_ids_list):
            df[f"level_{i+1}_id"] = tid
        tx = pd.concat([tx, df], ignore_index=True)

    name_cols = [c for c in tx.columns if not c.endswith("_id")]
    id_cols = [c for c in tx.columns if c.endswith("_id")]
    tx['most_specific_name'] = tx[name_cols].apply(lambda row: row.dropna().iloc[-1], axis=1)

    def get_last_id(row):
        """Return the ID corresponding to the rightmost non-NA name column."""
        mask = row[name_cols].notna()
        last_idx = mask[::-1].idxmax()
        id_col = last_idx + "_id"
        return row[id_col]

    tx['most_specific_id'] = tx.apply(get_last_id, axis=1)
    tx = tx.drop(columns=id_cols)
    return tx
