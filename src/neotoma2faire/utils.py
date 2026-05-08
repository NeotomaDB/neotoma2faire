# ---------------------------------------------------------------------------
# Excel / DB value formatting helpers
# ---------------------------------------------------------------------------

def format_db_value(v, none_placeholder=''):
    """Format a single database value for writing to a worksheet cell.

    Lists are joined with ``'; '`` after filtering out ``None`` entries.
    A bare ``None`` is replaced by *none_placeholder*.  All other values are
    returned unchanged.

    Args:
        v: The value to format.  May be a ``list``, ``None``, or a scalar.
        none_placeholder (str): String to use when *v* is ``None`` or an
            empty list.  Defaults to ``''``.

    Returns:
        str | Any: Formatted value suitable for an openpyxl cell.
    """
    if isinstance(v, list):
        filtered = [str(s) for s in v if s is not None]
        return '; '.join(filtered) if filtered else none_placeholder
    elif v is None:
        return none_placeholder
    return v


def write_sheet_rows(ws, df, header_row: int) -> None:
    """Write DataFrame rows into an openpyxl worksheet.

    Reads the column-name → column-index mapping from *header_row* of *ws*,
    then writes one data row per DataFrame row starting at ``header_row + 1``.
    Columns present in the sheet header but absent from *df* are skipped.
    ``NaN`` values are converted to ``None`` before writing.

    Uses ``df.to_dict(orient='records')`` internally so that column names
    containing spaces or special characters (e.g. ``'CRS (Calendar year)'``)
    are handled correctly.

    Args:
        ws: An openpyxl ``Worksheet``.
        df (pandas.DataFrame): Rows to write.
        header_row (int): 1-based row index of the column-name header in *ws*.
    """
    import pandas as pd  # local import to keep rpy2-free modules importable

    header = {cell.value: cell.column for cell in ws[header_row]}
    for row_idx, row_dict in enumerate(df.to_dict(orient="records"), start=header_row + 1):
        for col_name, col_idx in header.items():
            if col_name not in df.columns:
                continue
            value = row_dict.get(col_name)
            try:
                if pd.isna(value):
                    value = None
            except (TypeError, ValueError):
                pass
            try:
                ws.cell(row=row_idx, column=col_idx, value=value)
            except ValueError:
                ws.cell(row=row_idx, column=col_idx, value=None)


def add_sheet_from_dataset(wb, sheet_name: str, getter_fn, dataset_id: int, header_row: int = 3):
    """Fetch dataset rows via *getter_fn* and write them to *sheet_name*.

    A generic helper shared by :func:`~.add_amp_data.add_amp_data`,
    :func:`~.add_std_data.add_std_data`, and
    :func:`~.add_elow_quant.add_elow_quant`.  Each of those modules calls a
    different ``get_*`` function and targets a different sheet, but the
    surrounding logic is identical:

    1. Call ``getter_fn(dataset_id)`` → DataFrame.
    2. If the DataFrame is not empty, write it to ``wb[sheet_name]``.
    3. Return the DataFrame (empty or not) for the caller's use.

    Args:
        wb (openpyxl.Workbook): Target workbook.
        sheet_name (str): Name of the worksheet to populate.
        getter_fn (callable): A ``get_*(dataset_id) -> pd.DataFrame`` function.
        dataset_id (int): Neotoma dataset ID forwarded to *getter_fn*.
        header_row (int): 1-based row index of the column-name header in the
            target sheet.  Defaults to ``3``.

    Returns:
        pandas.DataFrame: The data written to the sheet, or an empty DataFrame
        if *getter_fn* returned no rows.
    """
    df = getter_fn(dataset_id)
    if not df.empty:
        write_sheet_rows(wb[sheet_name], df, header_row)
    return df
