def get_samples(df):
    """Pivot a long-format sample DataFrame to wide format.

    Selects the columns ``sampleid``, ``taxonid``, and ``value`` and pivots so
    that each unique ``sampleid`` becomes a column named ``sample_<id>``, with
    ``taxonid`` on the rows.

    Repeated ``(taxonid, sampleid)`` rows are **kept, not merged**: two taxa can
    share a name (and even an ASV label) while differing only by DNA sequence,
    which is not visible in these three columns, so collapsing or summing them
    would destroy distinct observations.  Each repeat is disambiguated by an
    occurrence counter and emitted as its own row (with ``taxonid`` repeated).

    Args:
        df (pandas.DataFrame): Long-format DataFrame containing at minimum
            the columns ``sampleid``, ``taxonid``, and ``value``.

    Returns:
        pandas.DataFrame: Wide-format DataFrame with ``taxonid`` as the first
        column and one ``sample_<sampleid>`` column per unique sample.
    """
    df = df[['sampleid', 'taxonid', 'value']].copy()
    df['occurrence'] = df.groupby(['taxonid', 'sampleid']).cumcount()
    wide = df.pivot(index=['taxonid', 'occurrence'], columns='sampleid', values='value')
    wide = wide.reset_index().drop(columns='occurrence')
    wide.columns = ['taxonid'] + [f'sample_{col}' for col in wide.columns[1:]]
    return wide
