"""Fetch eLow Quant scores from the imagined ndb.aednaelowquant table.

FAIRe ``eLowQuantData`` captures outputs from the eLow Quant pipeline for
low-copy-number eDNA samples: a numeric score, a classification (low / medium /
high), and a confidence value.  These fields have no equivalent in the current
Neotoma schema; this module queries the imagined table planned for the FAIRe
extension:

* ``ndb.aednaelowquant`` — one row per library × taxon eLow Quant result,
  linked to ``ndb.aednalibraries`` for the library identifier.
"""

import pandas as pd

#from ..utils import run_dataset_query

_QUERY = """
    SELECT
        lib.lib_id,
        lib.sampleid,
        eq.taxonid,
        eq.elowquant_score,
        eq.elowquant_class,
        eq.elowquant_conf
    FROM ndb.aednaelowquant AS eq
    JOIN ndb.aednalibraries AS lib
        ON lib.libraryid = eq.libraryid
    JOIN ndb.aednaassays AS aa
        ON aa.assayid = lib.assayid
    WHERE aa.datasetid = %(datasetid)s
    ORDER BY eq.elowquantid
"""


def get_elow_quant(dataset_id: int) -> pd.DataFrame:
    """Fetch eLow Quant scores for *dataset_id* from the imagined tables.

    Joins ``ndb.aednaelowquant`` to ``ndb.aednalibraries`` and
    ``ndb.aednaassays`` to return one row per library × taxon eLow Quant
    result.

    Returns an empty DataFrame when the imagined tables have not yet been
    populated, so callers can safely check :attr:`~pandas.DataFrame.empty`.

    Args:
        dataset_id (int): Neotoma dataset ID.

    Returns:
        pandas.DataFrame: Columns: ``lib_id``, ``sampleid``, ``taxonid``,
        ``elowquant_score``, ``elowquant_class``, ``elowquant_conf``.
        Empty DataFrame if no records exist.
    """
    # return run_dataset_query(_QUERY, dataset_id)
