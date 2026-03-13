import pandas as pd
from .get_samples import get_samples

def add_samples(wb, dsid, header_row=3):
    print(f"Adding sample data for datasetid {dsid} to workbook...")
    df = get_samples(dsid)
    return df
    # ws = wb['sampleMetadata']
    
    # # Read the header row to get column name -> column index mapping
    # header = {cell.value: cell.column for cell in ws[header_row]}
    
    # # Write data starting from the row after the header
    # for row_idx, row in enumerate(df.itertuples(index=False), start=header_row + 1):
    #     for col_name, col_idx in header.items():
    #         if col_name in df.columns:
    #             value = getattr(row, col_name, None)
    #             try:
    #                 if pd.isna(value):
    #                     value = None
    #             except (TypeError, ValueError):
    #                 value = None
    #             try:
    #                 ws.cell(row=row_idx, column=col_idx, value=value)
    #             except ValueError:
    #                 ws.cell(row=row_idx, column=col_idx, value=None)