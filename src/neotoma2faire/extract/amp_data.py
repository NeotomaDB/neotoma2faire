"""Fetch per-library amplification / qPCR data from the imagined ndb.aednaampdata table.

FAIRe ``ampData`` captures targeted amplification results: per-replicate Ct/Cq
values, estimated copy number, and detection call (positive / negative).  These
fields have no equivalent in the current Neotoma schema; this module queries the
imagined table planned for the FAIRe extension:

* ``ndb.aednaampdata`` — one row per library × taxon amplification event,
  linked back to ``ndb.aednalibraries`` for the library identifier and to
  ``ndb.taxa`` via ``taxonid``.
"""

import pandas as pd

#from ..utils import run_dataset_query

_QUERY = """
    SELECT
        lib.lib_id,
        lib.sampleid,
        amp.taxonid,
        amp.ct_cq,
        amp.copy_number,
        amp.detection_call
    FROM ndb.aednaampdata AS amp
    JOIN ndb.aednalibraries AS lib
        ON lib.libraryid = amp.libraryid
    JOIN ndb.aednaassays AS aa
        ON aa.assayid = lib.assayid
    WHERE aa.datasetid = %(datasetid)s
    ORDER BY lib.libraryid, amp.taxonid
"""


def get_amp_data(dataset_id: int) -> pd.DataFrame:
    """Fetch amplification/qPCR data for *dataset_id* from the imagined tables.

    Joins ``ndb.aednaampdata`` to ``ndb.aednalibraries`` and ``ndb.aednaassays``
    to return one row per library × taxon combination with Ct/Cq value, estimated
    copy number, and detection call.

    Returns an empty DataFrame when the imagined tables have not yet been
    populated, so callers can safely check :attr:`~pandas.DataFrame.empty`.

    Args:
        dataset_id (int): Neotoma dataset ID.

    Returns:
        pandas.DataFrame: Columns: ``lib_id``, ``sampleid``, ``taxonid``,
        ``ct_cq``, ``copy_number``, ``detection_call``.
        Empty DataFrame if no records exist.
    """
    ## return run_dataset_query(_QUERY, dataset_id)
    # The table this queries does not exist yet; return an empty frame so
    # callers can guard with .empty instead of tripping over None.
    return pd.DataFrame()
