"""Populate the taxa sheet with taxonomic hierarchy data.

The ``wb`` (workbook) parameter is accepted for future use — when the Excel
writing path is enabled the function will write directly into the taxa sheet.
For now the hierarchy result is returned as a DataFrame.
"""

from .get_taxa import get_taxa


def add_taxa(wb, txid, header_row=3):
    """Retrieve taxonomic hierarchy and (in future) write it to the workbook.

    Delegates to :func:`get_taxa` to build a wide-format DataFrame with one
    taxonomic-level column per ancestor plus ``most_specific_name`` and
    ``most_specific_id`` summary columns.

    Args:
        wb (openpyxl.Workbook): Target workbook.  Reserved for the Excel
            writing path; not used in the current implementation.
        txid (int | list[int]): One or more Neotoma taxon IDs to process.
        header_row (int): Row index (1-based) of the header in the taxa
            sheet.  Defaults to ``3``.

    Returns:
        pandas.DataFrame: One row per unique taxon ID, with ``level_N``
        name columns and ``most_specific_name`` / ``most_specific_id``
        summary columns.
    """
    df = get_taxa(txid)
    return df
