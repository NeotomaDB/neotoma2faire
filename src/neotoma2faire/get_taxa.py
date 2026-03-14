import rpy2.robjects as ro
from rpy2.robjects.packages import importr
from rpy2.robjects import pandas2ri
import pandas as pd

neo2 = importr('neotoma2')

def _r_to_df(r_obj):
    """Convert an R object to a pandas DataFrame."""
    df = ro.r('function(x) as.data.frame(x)')(r_obj)
    return pandas2ri.rpy2py(df)

taxa_tbl = neo2.get_table('taxa', limit=65000)
taxa_df = _r_to_df(taxa_tbl)

def climb_up(start_id, taxa=taxa_df):
    taxa = taxa.set_index('taxonid').to_dict(orient='index')
    path = []
    visited = set()
    current = start_id
    level = 1
    while current is not None and current not in visited:
        visited.add(current)
        node = taxa.get(current)
        if not node:
            break
        path.append({
            "level": level,
            "taxonid": current,
            "taxonname": node["taxonname"]
        })
        parent = node["highertaxonid"]
        if parent is None or parent == current:
            break
        current = parent
        level += 1
    return path

def get_taxa(taxa_ids):
    if isinstance(taxa_ids, int):
        taxa_ids = [taxa_ids]
    taxa_ids = list(set(taxa_ids)) 
    tx = pd.DataFrame()
    for taxon_id in taxa_ids:
        hierarchy = climb_up(taxon_id)
        path_sorted = sorted(hierarchy, key=lambda x: x["level"], reverse=True)
        taxon_names = [node["taxonname"] for node in path_sorted]
        taxon_ids_list = [node["taxonid"] for node in path_sorted]
        df = pd.DataFrame([taxon_names], columns=[f"level_{i+1}" for i in range(len(taxon_names))])
        for i, tid in enumerate(taxon_ids_list):
            df[f"level_{i+1}_id"] = tid
        tx = pd.concat([tx, df], ignore_index=True)
    
    name_cols = [c for c in tx.columns if not c.endswith("_id")]
    id_cols = [c for c in tx.columns if c.endswith("_id")]
    print(tx.head(2))
    tx['most_specific_name'] = tx[name_cols].apply(lambda row: row.dropna().iloc[-1], axis=1)
    print('here')
    print(tx.head(2))
    # Corresponding ID

    def get_last_id(row):
        # Mask of which name columns are not NA
        mask = row[name_cols].notna()
        # Position of the last non-NA column
        last_idx = mask[::-1].idxmax()  # reversed, so idxmax gives the rightmost
        # idxmax returns column name, map to corresponding ID column
        id_col = last_idx + "_id"
        return row[id_col]

    tx['most_specific_id'] = tx.apply(get_last_id, axis=1)
    tx = tx.drop(columns=id_cols)
    return tx
