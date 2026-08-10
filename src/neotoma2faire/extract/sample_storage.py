"""Fetch per-sample storage metadata from the imagined ndb.samplestorage tables.

This module queries four imagined Neotoma tables that do not yet exist in the
production schema but are part of the planned FAIRe extension:

* ``ndb.samplestorage`` — links samples to storage conditions and sample
  category / control-type classifications.
* ``ndb.samplecategories`` — controlled vocabulary: sample, negative control,
  positive control, PCR standard, other.
* ``ndb.negativecontroltypes`` — controlled vocabulary: site negative, field
  negative, process negative, extraction negative, PCR negative, other.
* ``ndb.samplestoragesolutions`` — controlled vocabulary: ethanol, sodium
  acetate, longmire, lysis buffer, none, other.
* ``ndb.spatialreferencesystems`` — controlled vocabulary: WGS84, NAD84,
  NAD27, GDA94, GDA2020, ETRS89, JGD2000, other.

The result is intended to be merged into the per-sample metadata DataFrame
produced by :func:`~.get_sample_metadata.get_sample_metadata` so that
:func:`~.add_samples.add_samples` can write all storage-related FAIRe fields
to the ``sampleMetadata`` sheet.
"""

import pandas as pd

#from ..utils import run_dataset_query

_QUERY = """
    SELECT
        ss.sampleid,
        sc.samplecategory            AS samp_category,
        nc.negativecontroltype       AS neg_cont_type,
        sol.samplestoragesolution    AS samp_store_sol,
        ss.samp_store_loc,
        ss.samp_store_temp,
        ss.samp_store_dur,
        ss.dna_store_loc,
        srs.spatialreferencesystem   AS "verbatimSRS"
    FROM ndb.samplestorage AS ss
    JOIN ndb.samples AS s
        ON s.sampleid = ss.sampleid
    JOIN ndb.analysisunits AS au
        ON au.analysisunitid = s.analysisunitid
    JOIN ndb.collectionunits AS cu
        ON cu.collectionunitid = au.collectionunitid
    JOIN ndb.datasets AS ds
        ON ds.collectionunitid = cu.collectionunitid
    LEFT JOIN ndb.samplecategories AS sc
        ON sc.samplecategoryid = ss.samplecategoryid
    LEFT JOIN ndb.negativecontroltypes AS nc
        ON nc.negativecontroltypeid = ss.negativecontroltypeid
    LEFT JOIN ndb.samplestoragesolutions AS sol
        ON sol.samplestoragesolutionid = ss.samplestoragesolutionid
    LEFT JOIN ndb.spatialreferencesystems AS srs
        ON srs.spatialreferencesystemid = ss.spatialreferencesystemid
    WHERE ds.datasetid = %(datasetid)s
    ORDER BY ss.sampleid
"""


def get_sample_storage(dataset_id: int) -> pd.DataFrame:
    """Fetch per-sample storage metadata for *dataset_id*.

    Queries the imagined ``ndb.samplestorage`` table joined to its controlled-
    vocabulary lookup tables to return one row per sample with FAIRe storage
    and sample-category fields.

    Returns an empty DataFrame when no storage records exist for the dataset
    (e.g., the imagined tables have not yet been populated), so callers can
    safely check :attr:`~pandas.DataFrame.empty` without special-casing.

    Args:
        dataset_id (int): Neotoma dataset ID.

    Returns:
        pandas.DataFrame: Columns: ``sampleid``, ``samp_category``,
        ``neg_cont_type``, ``samp_store_sol``, ``samp_store_loc``,
        ``samp_store_temp``, ``samp_store_dur``, ``dna_store_loc``,
        ``verbatimSRS``.  Empty DataFrame if no storage records exist.
    """
    # return run_dataset_query(_QUERY, dataset_id)
    # The table this queries does not exist yet; return an empty frame so
    # callers can guard with .empty instead of tripping over None.
    return pd.DataFrame()
