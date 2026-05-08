"""Build taxonomic hierarchy tables from Neotoma taxa data.

Uses the Neotoma REST API v2.0 to fetch taxa on demand rather than loading the
full 65 000-row table at import time.  A module-level dict caches each taxon
after its first fetch so repeated calls for the same IDs are free.

Public helpers:

* :func:`climb_up` — walk the parent-child hierarchy upward from a single
  taxon ID and return the ordered path.
* :func:`get_taxa` — process a list of taxon IDs and return a DataFrame with
  one column per taxonomic level plus ``most_specific_name`` /
  ``most_specific_id`` convenience columns.
"""

import pandas as pd

from ..api.client import get_taxa_batch

# Module-level cache: taxonid (int) → {"taxonname": str, "highertaxonid": int|None}
_taxa_cache: dict[int, dict] = {}


def _ensure_taxa(taxon_ids: list[int]) -> None:
    """Fetch any taxon IDs not yet present in the module-level cache.

    Args:
        taxon_ids (list[int]): IDs to guarantee are in ``_taxa_cache``.
    """
    missing = [tid for tid in taxon_ids if tid not in _taxa_cache]
    if not missing:
        return
    for t in get_taxa_batch(missing):
        _taxa_cache[int(t["taxonid"])] = {
            "taxonname": t.get("taxonname"),
            "highertaxonid": t.get("highertaxonid"),
        }


def climb_up(start_id: int, taxa: "pd.DataFrame | None" = None) -> list[dict]:
    """Walk the taxonomic hierarchy upward from *start_id*.

    Traverses the ``highertaxonid`` parent links starting at *start_id*,
    collecting each node until the root is reached, a cycle is detected, or a
    missing node is encountered.

    When *taxa* is ``None`` (the default), parent nodes are fetched via the
    Neotoma API on demand and stored in the module-level ``_taxa_cache``.
    Pass an explicit DataFrame (with columns ``taxonid``, ``taxonname``,
    ``highertaxonid``) to bypass the API entirely — useful in tests.

    Args:
        start_id (int): Neotoma ``taxonid`` of the taxon to start from.
        taxa (pandas.DataFrame | None): Optional explicit taxa table.  When
            provided, the API cache is not consulted.  Defaults to ``None``.

    Returns:
        list[dict]: Ordered list of nodes from *start_id* upward, where each
        node is a dict with keys ``level`` (int, starting at 1 = most
        specific), ``taxonid`` (int), and ``taxonname`` (str).
    """
    # Build a lookup from either the supplied DataFrame or the module cache
    if taxa is not None:
        lookup: dict[int, dict] = taxa.set_index("taxonid").to_dict(orient="index")
    else:
        lookup = None  # type: ignore[assignment]  # sentinel: use cache

    path: list[dict] = []
    visited: set[int] = set()
    current: int | None = start_id
    level = 1

    while current is not None and current not in visited:
        if lookup is not None:
            node = lookup.get(current)
        else:
            _ensure_taxa([current])
            node = _taxa_cache.get(current)
        if not node:
            break
        visited.add(current)
        path.append({"level": level, "taxonid": current, "taxonname": node["taxonname"]})
        parent = node.get("highertaxonid")
        # pandas converts None in integer columns to float NaN; handle both
        try:
            is_null = parent is None or (parent != parent)  # NaN != NaN
        except TypeError:
            is_null = False
        if is_null or parent == current:
            break
        current = parent
        level += 1

    return path


def get_taxa(taxa_ids: int | list[int]) -> pd.DataFrame:
    """Build a hierarchical taxa DataFrame for a list of taxon IDs.

    For each ID in *taxa_ids*, :func:`climb_up` is called to retrieve the
    full ancestry path.  The results are assembled into a DataFrame where
    each column ``level_N`` holds the taxon name at depth *N* (1 = root /
    least specific, higher numbers = more derived / most specific).  Two
    summary columns are added:

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

    # Pre-fetch all leaf taxa in one batch for efficiency
    _ensure_taxa(taxa_ids)

    tx = pd.DataFrame()
    for taxon_id in taxa_ids:
        hierarchy = climb_up(taxon_id)
        # Sort from least specific (highest level number = root) to most specific
        path_sorted = sorted(hierarchy, key=lambda x: x["level"], reverse=True)
        taxon_names = [node["taxonname"] for node in path_sorted]
        taxon_ids_list = [node["taxonid"] for node in path_sorted]
        df = pd.DataFrame([taxon_names], columns=[f"level_{i + 1}" for i in range(len(taxon_names))])
        for i, tid in enumerate(taxon_ids_list):
            df[f"level_{i + 1}_id"] = tid
        tx = pd.concat([tx, df], ignore_index=True)

    name_cols = [c for c in tx.columns if not c.endswith("_id")]
    id_cols = [c for c in tx.columns if c.endswith("_id")]
    tx["most_specific_name"] = tx[name_cols].apply(lambda row: row.dropna().iloc[-1], axis=1)

    def get_last_id(row):
        """Return the taxon ID corresponding to the rightmost non-NA name column."""
        mask = row[name_cols].notna()
        last_idx = mask[::-1].idxmax()
        id_col = last_idx + "_id"
        return row[id_col]

    tx["most_specific_id"] = tx.apply(get_last_id, axis=1)
    tx = tx.drop(columns=id_cols)
    return tx
