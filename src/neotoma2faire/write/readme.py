"""Stamp the README sheet with the tool version and current timestamp.

Called as part of the template-generation workflow to record when and by
which version of neotoma2FAIRe the workbook was last modified.
"""

from datetime import datetime


def modify_README(workbook):
    """Insert version and timestamp rows into the README sheet.

    Inserts two new rows after row 2 of the ``README`` sheet and writes the
    tool name/version and the current datetime.

    Args:
        workbook (openpyxl.Workbook): Workbook whose ``README`` sheet will
            be updated.  The sheet must already exist.

    Returns:
        openpyxl.Workbook: The same workbook with the README sheet updated.
    """
    ws = workbook.active = workbook['README']

    ws.insert_rows(3, 2)
    ws['A4'] = 'Modified by:'
    ws['A5'] = 'neotoma2FAIRe v0.1.0'
    ws.insert_rows(6, 1)
    ws['A8'] = datetime.now()
    return workbook
