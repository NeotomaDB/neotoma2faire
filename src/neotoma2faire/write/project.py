"""Populate the projectMetadata sheet with dataset provenance information.

Queries the Neotoma REST API v2.0 (no database credentials required) for the
project(s) linked to a dataset and their participants, then maps the results
onto the ``projectMetadata`` worksheet using the ``term_name`` → row mapping
already present in that sheet.

The ``projectMetadata`` sheet is a *vertical* metadata table: each FAIRe term
occupies its own *row* (``term_name`` in column C), and the populated value goes
in column D (``project_level``).

Only terms backed by production Neotoma tables are written (``project_id``,
``recordedBy``, ``project_contact``).  The PCR/assay/sequencing terms come from
tables that do not exist yet and are left blank.
"""

from ..api.client import get_dataset, get_projects_by_dataset
from ..utils import format_db_value


def add_project(workbook, datasetid: int):
    """Write project metadata for *datasetid* into the workbook.

    Reads the ``term_name`` column of the ``projectMetadata`` sheet to build a
    row-index lookup, then calls ``GET /datasets/{id}/projects`` to fill
    ``project_id``, ``recordedBy``, and ``project_contact``.  When no project is
    linked, falls back to the dataset PI list so ``recordedBy`` is still filled.

    Args:
        workbook (openpyxl.Workbook): Workbook whose ``projectMetadata`` sheet
            will be populated.
        datasetid (int): Neotoma dataset ID whose provenance should be written.

    Returns:
        openpyxl.Workbook: The same workbook with ``projectMetadata`` updated.
    """
    ws = workbook["projectMetadata"]

    # term_name (column C) → 1-based sheet row.
    term_row = {
        ws.cell(r, 3).value: r
        for r in range(2, ws.max_row + 1)
        if ws.cell(r, 3).value
    }

    def set_term(term, value):
        # Leave the cell null when there is nothing to write.
        formatted = format_db_value(value)
        row = term_row.get(term)
        if row is not None and formatted != "":
            ws.cell(row, 4, value=formatted)

    projects = get_projects_by_dataset(datasetid)
    project = projects[0] if projects else {}
    participants = project.get("participants", [])

    set_term("project_id", project.get("projectname"))
    set_term("project_contact", [p.get("email") for p in participants])

    # recordedBy: project participants when present, else the dataset PI list.
    names = [p.get("contactname") for p in participants]
    if not any(names):
        datasets = get_dataset(datasetid).get("datasets", [])
        pis = datasets[0].get("datasetpi", []) if datasets else []
        names = [pi.get("contactname") for pi in pis]
    set_term("recordedBy", names)

    return workbook
