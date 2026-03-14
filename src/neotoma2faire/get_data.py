"""Fetch and assemble a Neotoma dataset into a single flat DataFrame.

The public entry point is :func:`get_data`, which calls the ``neotoma2`` R
package via rpy2 to retrieve site, collection-unit, dataset, sample, lake-
parameter, and geopolitical-unit records, then merges them into one tidy
DataFrame ready for downstream processing.
"""

from rpy2.robjects.packages import importr
import pandas as pd
import numpy as np

from .utils import _r_to_df, _r_subset

neo2 = importr('neotoma2')


def get_data(dsid):
    """Download a Neotoma dataset and return a merged, cleaned DataFrame.

    Uses the ``neotoma2`` R package to retrieve all records associated with
    *dsid*, then merges site metadata, collection-unit metadata, dataset
    metadata, sample data, lake parameters, and geopolitical units into a
    single deduplicated DataFrame.

    Args:
        dsid (int): Neotoma dataset ID to download.

    Returns:
        pandas.DataFrame: One row per sample × taxon combination, with
        columns for site, collection unit, dataset, depth, geopolitical name,
        and water-column depth (``tot_depth_water_col``).
    """
    st_dl = neo2.get_downloads(dsid)

    # ==== Site Metadata ====
    st_df = _r_to_df(st_dl)
    siteid = int(st_df['siteid'].iloc[0])

    # ==== CU Metadata ====
    cu_df = _r_to_df(neo2.collunits(st_dl))

    # ==== DS Metadata ====
    ds_df = _r_to_df(neo2.datasets(st_dl))

    # ==== Sample Data ====
    st_samp = pd.DataFrame(_r_to_df(neo2.samples(st_dl)))

    # ==== Lake Params ====
    # TODO: There is API for ap.hydrolakes but not for ndb.lakeparameters
    # TODO: R Function `get_lakeparams` needs to be created to filter by siteid
    lk = neo2.get_table('lakeparameters', limit=30000)
    lk_df = _r_to_df(_r_subset(lk, f'siteid == {siteid} & lakeparameterid == 1'))

    # ==== GPUID Params ====
    # TODO: API integration of GPUIDs and R function.
    st_gp = neo2.get_table('sitegeopolitical', limit=70000)
    st_gp = _r_to_df(_r_subset(st_gp, f'siteid == {siteid}'))
    gp_ids_r = ', '.join(map(str, st_gp['geopoliticalid'].unique()))

    gpuid = neo2.get_table('geopoliticalunits', limit=12000)
    gpuid_df = _r_to_df(_r_subset(gpuid, f'geopoliticalid %in% c({gp_ids_r})'))

    st_gp = (
        st_gp.merge(gpuid_df, on='geopoliticalid', how='left')
        .groupby('siteid')['geopoliticalname']
        .apply(', '.join)
        .reset_index()
    )

    # ==== Merge all dataframes ====
    st_samp = (
        st_samp
        .merge(st_df, on='siteid', how='left', suffixes=('', '_st'))
        .merge(cu_df, left_on='collunitid', right_on='collectionunitid', how='left')
        .merge(ds_df, on='datasetid', how='left', suffixes=('', '_ds'))
        .merge(lk_df[['siteid', 'value']], on='siteid', how='left', suffixes=('', '_lk'))
        .merge(st_gp, on='siteid', how='left')
    )

    # ==== Clean and match template ====
    st_samp = st_samp.replace(r'^NA_.*$', np.nan, regex=True)
    st_samp['samp_category'] = 'sample'
    st_samp['minimumDepthInMeters'] = st_samp['depth']
    st_samp['maximumDepthInMeters'] = st_samp['depth']
    st_samp['geo_loc_name'] = st_samp['geopoliticalname']
    st_samp = st_samp.rename(columns={'value_lk': 'tot_depth_water_col'})
    samples_df = st_samp.drop_duplicates()

    return samples_df
