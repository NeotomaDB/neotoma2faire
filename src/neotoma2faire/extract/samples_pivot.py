def get_samples(df):
    """Pivot a long-format sample DataFrame to wide format.

    Selects the columns ``sampleid``, ``taxonid``, and ``value``, drops
    duplicate rows, then pivots so that each unique ``sampleid`` becomes a
    column named ``sample_<id>``, with ``taxonid`` as the row index.

    Args:
        df (pandas.DataFrame): Long-format DataFrame containing at minimum
            the columns ``sampleid``, ``taxonid``, and ``value``.

    Returns:
        pandas.DataFrame: Wide-format DataFrame with ``taxonid`` as the first
        column and one ``sample_<sampleid>`` column per unique sample.
    """
    df = df[['sampleid', 'taxonid', 'value']].drop_duplicates()
    df = df.pivot(index='taxonid', columns='sampleid', values='value').reset_index()
    df.columns = ['taxonid'] + [f'sample_{col}' for col in df.columns if col != 'taxonid']
    return df
