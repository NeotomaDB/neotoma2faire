def get_samples(df):
    df = df[['sampleid', 'taxonid', 'value']].drop_duplicates()
    df = df.pivot(index='taxonid', columns='sampleid', values='value').reset_index()
    df.columns = ['taxonid'] + [f'sample_{col}' for col in df.columns if col != 'taxonid']
    
    return df