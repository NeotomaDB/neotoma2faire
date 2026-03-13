import rpy2.robjects as ro
from rpy2.robjects.packages import importr
from rpy2.robjects import pandas2ri
import pandas as pd
import numpy as np

neo2 = importr('neotoma2')


def _r_to_df(r_obj):
    """Convert an R object to a pandas DataFrame."""
    df = ro.r('function(x) as.data.frame(x)')(r_obj)
    return pandas2ri.rpy2py(df)


def _r_subset(r_obj, condition):
    """Subset an R object using an R expression string."""
    return ro.r(f'function(x) subset(x, {condition})')(r_obj)


def get_samples(dsid):
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
    
    # ==== Pivot to wide format ====
    index_cols = ['sampleid', 'depth', 'age']
    skip = set(index_cols + ['variablename', 'value', 'units'])
    meta_cols = [c for c in samples_df.columns if c not in skip]
    meta_df = samples_df[['sampleid'] + meta_cols].drop_duplicates(subset=['sampleid'])

    vals_df = samples_df.pivot(
        index=index_cols,
        columns='variablename',
        values='value', # add units
        ).reset_index()
    
    units_df = samples_df.pivot(
        index=index_cols,
        columns='variablename',
        values='units').reset_index()
    units_df = units_df.rename(
    columns={c: f"{c}_units" for c in units_df.columns if c not in index_cols})
    val_taxa = [c for c in vals_df.columns if c not in index_cols]
    ordered = index_cols + [
    col for t in val_taxa for col in (t, f"{t}_units")]
    samples_df = vals_df.merge(units_df, on=index_cols, how='left')
    samples_df = samples_df[ordered]

    desired_meta = [
    'sampleid', 'siteid', 'sitename', 'latitude', 'lat', 'longitude', 'long',
    'elevation', 'elev', 'geo_loc_name', 'collunitid', 'handle', 'colldate',
    'waterdepth', 'collunittype', 'collectiondevice', 'datasetid', 'datasetname',
    'datasettype', 'samp_category', 'maximumDepthInMeters', 'minimumDepthInMeters',
    'tot_depth_water_col', 'geopoliticalname']
    
    available = [c for c in desired_meta if c in meta_df.columns]
    meta_df = meta_df[available].drop_duplicates(subset=['sampleid'])
    
    return meta_df.merge(samples_df, on='sampleid', how='right')
