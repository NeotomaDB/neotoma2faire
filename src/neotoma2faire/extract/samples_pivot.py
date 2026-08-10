def get_samples(df, keep_occurrence: bool = False):
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
        keep_occurrence (bool): When ``True``, keep the occurrence counter as a
            column so callers can pair the *n*-th repeat of a taxon with the
            *n*-th of whatever distinguishes it (a DNA sequence, say).
            Defaults to ``False``.

    Returns:
        pandas.DataFrame: Wide-format DataFrame with ``taxonid`` as the first
        column (followed by ``occurrence`` when *keep_occurrence*) and one
        ``sample_<sampleid>`` column per unique sample.
    """
    df = df[['sampleid', 'taxonid', 'value']].copy()
    df['occurrence'] = df.groupby(['taxonid', 'sampleid']).cumcount()
    wide = df.pivot(index=['taxonid', 'occurrence'], columns='sampleid', values='value')
    wide = wide.reset_index()
    index_cols = ['taxonid', 'occurrence'] if keep_occurrence else ['taxonid']
    if not keep_occurrence:
        wide = wide.drop(columns='occurrence')
    wide.columns = index_cols + [f'sample_{col}' for col in wide.columns[len(index_cols):]]
    return wide
