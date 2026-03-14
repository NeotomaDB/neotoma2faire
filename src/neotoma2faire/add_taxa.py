import pandas as pd
from .get_taxa import get_taxa

def add_taxa(wb, txid, header_row=3):
    df = get_taxa(txid)

    return df