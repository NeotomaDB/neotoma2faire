"""Stamp the README sheet with the tool name and generation timestamp.

Records who generated the workbook (neotoma2FAIRe + version) and when, so a
downloaded FAIRe workbook carries its own provenance.
"""

from datetime import datetime

_VERSION = "0.1.0"


def modify_README(workbook, checklist_version: str | None = None):
    """Write the checklist version, "Modified by" and generation time into README.

    A1 reads "The templates were generated using the FAIR eDNA checklist
    version of;" and A2 is that prompt's answer slot — blank in the pristine
    template — so the checklist version goes there and the tool stamp goes on
    the following line.

    Args:
        workbook (openpyxl.Workbook): Workbook whose ``README`` sheet will be
            updated.  The sheet must already exist.
        checklist_version (str | None): FAIRe checklist version the workbook was
            built from, from :func:`~.utils.checklist_version`.  When ``None``,
            A2 is left as the template had it.

    Returns:
        openpyxl.Workbook: The same workbook with the README sheet updated.
    """
    ws = workbook["README"]
    if checklist_version is not None:
        ws["A2"] = checklist_version
    ws["A3"] = f"Modified by: Neotoma2FAIRe v{_VERSION}"
    ws["A4"] = "Date/Time generated:"
    ws["B4"] = datetime.now()
    return workbook
