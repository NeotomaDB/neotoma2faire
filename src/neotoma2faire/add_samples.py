"""Populate the sampleMetadata sheet with pivoted sample data.

The ``wb`` (workbook) parameter is accepted for future use — when the Excel
writing path is enabled the function will write directly into the
``sampleMetadata`` sheet.  For now the pivot result is returned as a
DataFrame.
"""

from .get_samples import get_samples


def add_samples(wb, df, header_row=3):
    """Pivot sample data and (in future) write it to the workbook.

    Delegates to :func:`get_samples` to produce a wide-format DataFrame
    (taxa as rows, samples as columns named ``sample_<id>``).

    Args:
        wb (openpyxl.Workbook): Target workbook.  Reserved for the Excel
            writing path; not used in the current implementation.
        df (pandas.DataFrame): Long-format DataFrame containing at minimum
            the columns ``sampleid``, ``taxonid``, and ``value``.
        header_row (int): Row index (1-based) of the header in the
            ``sampleMetadata`` sheet.  Defaults to ``3``.

    Returns:
        pandas.DataFrame: Wide-format pivot with one row per taxon and one
        column per sample.
    """
    df = get_samples(df)
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
