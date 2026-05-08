"""Fetch PCR standard curve data from the imagined ndb.aednastddata table.

FAIRe ``stdData`` captures the standard curve parameters used to quantify
DNA copy numbers from Ct/Cq values: input quantity (copies / µL), amplification
efficiency, and R² of the fitted curve.  These fields have no equivalent in the
current Neotoma schema; this module queries the imagined table planned for the
FAIRe extension:

* ``ndb.aednastddata`` — one row per assay standard measurement, linked to
  ``ndb.aednaassays`` for the assay context (target gene, subfragment).
"""

import pandas as pd

#from ..utils import run_dataset_query

_QUERY = """
    SELECT
        std.stddataid,
        aa.assayid,
        aa.target_gene,
        aa.subfragment,
        std.input_quantity,
        std.efficiency,
        std.r_squared
    FROM ndb.aednastddata AS std
    JOIN ndb.aednaassays AS aa
        ON aa.assayid = std.assayid
    WHERE aa.datasetid = %(datasetid)s
    ORDER BY std.stddataid
"""


def get_std_data(dataset_id: int) -> pd.DataFrame:
    """Fetch PCR standard curve data for assays linked to *dataset_id*.

    Joins ``ndb.aednastddata`` to ``ndb.aednaassays`` to return one row per
    standard-curve measurement with input quantity, amplification efficiency,
    and R² of the curve fit.

    Returns an empty DataFrame when the imagined tables have not yet been
    populated, so callers can safely check :attr:`~pandas.DataFrame.empty`.

    Args:
        dataset_id (int): Neotoma dataset ID.

    Returns:
        pandas.DataFrame: Columns: ``stddataid``, ``assayid``, ``target_gene``,
        ``subfragment``, ``input_quantity``, ``efficiency``, ``r_squared``.
        Empty DataFrame if no records exist.
    """
    return run_dataset_query(_QUERY, dataset_id)
