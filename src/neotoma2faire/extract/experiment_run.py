"""Fetch experiment run metadata from the imagined ndb.aednaassays and ndb.aednalibraries tables.

FAIRe ``experimentRunMetadata`` captures per-library sequencing metadata such as
assay type, target gene, primer sequences, library layout, and sequencing method.
In the current production Neotoma schema these fields do not exist; this module
queries the imagined tables that will hold them once the FAIRe extension is deployed:

* ``ndb.aednaassays`` — assay configuration per dataset (target gene, subfragment,
  primer names, library layout, sequencing method, assay type FK).
* ``ndb.aednalibraries`` — per-sample × assay library record (lib_id, seq_run_id).
* ``ndb.assaytypes`` — controlled vocabulary: targeted, metabarcoding, other.

The returned DataFrame is intended to supplement the basic ``samp_name`` /
``assay_name`` rows already written by :func:`~.add_experiment_run.add_experiment_run`
with the richer sequencing-pipeline metadata stored in the imagined tables.
"""

import pandas as pd

#from ..utils import run_dataset_query

_QUERY = """
    SELECT
        s.samplename                    AS samp_name,
        lib.lib_id,
        lib.seq_run_id,
        at.assaytype                    AS assay_type,
        aa.target_gene,
        aa.subfragment,
        aa.pcr_primer_name_forward,
        aa.pcr_primer_name_reverse,
        aa.lib_layout,
        aa.seq_meth
    FROM ndb.aednalibraries AS lib
    JOIN ndb.aednaassays AS aa
        ON aa.assayid = lib.assayid
    JOIN ndb.assaytypes AS at
        ON at.assaytypeid = aa.assaytypeid
    JOIN ndb.samples AS s
        ON s.sampleid = lib.sampleid
    WHERE aa.datasetid = %(datasetid)s
    ORDER BY lib.sampleid, lib.libraryid
"""


def get_experiment_run(dataset_id: int) -> pd.DataFrame:
    """Fetch experiment run metadata for *dataset_id* from the imagined tables.

    Joins ``ndb.aednalibraries`` to ``ndb.aednaassays`` and ``ndb.assaytypes``
    to produce one row per sample × library combination, including assay type,
    target gene, primer names, library layout, and sequencing method.

    Returns an empty DataFrame when the imagined tables have not yet been
    populated, so callers can safely check :attr:`~pandas.DataFrame.empty`.

    Args:
        dataset_id (int): Neotoma dataset ID.

    Returns:
        pandas.DataFrame: Columns: ``samp_name``, ``lib_id``, ``seq_run_id``,
        ``assay_type``, ``target_gene``, ``subfragment``,
        ``pcr_primer_name_forward``, ``pcr_primer_name_reverse``,
        ``lib_layout``, ``seq_meth``.  Empty DataFrame if no records exist.
    """
    # return run_dataset_query(_QUERY, dataset_id)
    # The table this queries does not exist yet; return an empty frame so
    # callers can guard with .empty instead of tripping over None.
    return pd.DataFrame()
