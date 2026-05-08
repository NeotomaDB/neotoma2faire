"""Fetch ASV/sequence records from the imagined ndb.aednasequences table.

FAIRe ``taxaRaw`` and ``taxaFinal`` carry sequence-level taxonomy assignments
for each ASV or OTU: the assigned scientific name, match identity (pident),
query coverage (qcovs), reference database, and the raw sequence itself.
None of these fields exist in the current Neotoma schema; this module queries
the imagined table that will hold them:

* ``ndb.aednasequences`` — one row per ASV/OTU × library, with a boolean
  ``is_curated`` flag that separates raw assignments (``taxaRaw``) from
  curated, publication-quality assignments (``taxaFinal``).

The two FAIRe sheets are populated by passing ``curated=False`` and
``curated=True`` respectively to :func:`get_taxa_sequences`.
"""

import pandas as pd

##from ..utils import run_dataset_query

_QUERY = """
    SELECT
        seq.seq_id,
        seq.asv_sequence,
        seq.taxonid,
        seq.pident,
        seq.qcovs,
        seq.reference_db,
        seq.reference_sequence,
        seq.is_curated,
        lib.lib_id,
        lib.sampleid
    FROM ndb.aednasequences AS seq
    JOIN ndb.aednalibraries AS lib
        ON lib.libraryid = seq.libraryid
    JOIN ndb.aednaassays AS aa
        ON aa.assayid = lib.assayid
    WHERE aa.datasetid = %(datasetid)s
      AND seq.is_curated = %(is_curated)s
    ORDER BY seq.sequenceid
"""


def get_taxa_sequences(dataset_id: int, curated: bool = False) -> pd.DataFrame:
    """Fetch ASV/OTU sequence records for *dataset_id*.

    Queries ``ndb.aednasequences`` joined to ``ndb.aednalibraries`` and
    ``ndb.aednaassays``.  The ``curated`` flag selects between raw (uncurated)
    and final (curated) sequence assignments, corresponding to FAIRe
    ``taxaRaw`` and ``taxaFinal`` respectively.

    Returns an empty DataFrame when the imagined tables have not yet been
    populated, so callers can safely check :attr:`~pandas.DataFrame.empty`.

    Args:
        dataset_id (int): Neotoma dataset ID.
        curated (bool): When ``False`` (default), returns uncurated records
            for ``taxaRaw``.  When ``True``, returns curated records for
            ``taxaFinal``.

    Returns:
        pandas.DataFrame: Columns: ``seq_id``, ``asv_sequence``, ``taxonid``,
        ``pident``, ``qcovs``, ``reference_db``, ``reference_sequence``,
        ``is_curated``, ``lib_id``, ``sampleid``.
        Empty DataFrame if no records exist.
    """
    # Build a query with the is_curated literal embedded so run_dataset_query
    # can be used unchanged (it only substitutes %(datasetid)s).
    curated_literal = "TRUE" if curated else "FALSE"
    query = _QUERY.replace("%(is_curated)s", curated_literal)
    # return run_dataset_query(query, dataset_id)
