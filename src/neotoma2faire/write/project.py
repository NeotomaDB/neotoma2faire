"""Populate the projectMetadata sheet with dataset provenance information.

Queries the Neotoma REST API v2.0 (no database credentials required) for PI
contacts, publications, and project details, then maps the results onto the
``projectMetadata`` worksheet using the ``term_name`` → row mapping already
present in that sheet.

The ``projectMetadata`` sheet is a *vertical* metadata table: each FAIRe term
occupies its own *row*, and the populated value goes in column D
(``project_level``).
"""

from ..api.client import get_contact, get_dataset, get_publications
#from ..utils import apply_query_result

def add_project(workbook, datasetid: int):
    """Write project metadata for *datasetid* into the workbook.

    Reads the ``term_name`` column of the ``projectMetadata`` sheet to build a
    row-index lookup, then calls the Neotoma API to collect PI names/IDs,
    institutional addresses, publication citations, and the default CC-BY
    license string.  Results are written to column D (``project_level``) via
    :func:`~.utils.apply_query_result`.

    Args:
        workbook (openpyxl.Workbook): Workbook whose ``projectMetadata`` sheet
            will be populated.
        datasetid (int): Neotoma dataset ID whose provenance should be written.

    Returns:
        openpyxl.Workbook: The same workbook with ``projectMetadata`` updated.
    """
    ws = workbook.active = workbook["projectMetadata"]

    # Build term_name → row-index mapping from the existing sheet structure
    keys = [ws.cell(1, i).value for i in range(1, ws.max_column + 1)]
    celltodict = []
    for row in range(2, ws.max_row + 1):
        tempdict = {}
        for i in range(1, ws.max_column + 1):
            tempdict[keys[i - 1]] = ws.cell(row, i).value
        celltodict.append(tempdict)

    term_row_map = {entry["term_name"]: j for j, entry in enumerate(celltodict) if entry.get("term_name")}

    def write_project(_row_idx, j, value):
        celltodict[j]["project_level"] = value
        ws.cell(j + 2, 4, value=value)  # column D; +2 for header row + 1-based index

    # --- PI contacts from the datasets endpoint ---
    site_data = get_dataset(datasetid)
    datasets = site_data.get("datasets", [])
    ds = datasets[0] if datasets else {}
    pis = ds.get("datasetpi", [])

    contact_names = [pi["contactname"] for pi in pis]
    contact_ids = [str(pi["contactid"]) for pi in pis]

    # Fetch full contact records to extract institution from address field
    institutions: list[str] = []
    for pi in pis:
        contact = get_contact(pi["contactid"])
        addr = contact.get("address") or ""
        # First non-empty line of address is typically the institution name
        first_line = next((ln.strip() for ln in addr.splitlines() if ln.strip()), None)
        if first_line:
            institutions.append(first_line)

    project_result = [
        {
            "recordedBy": contact_names,
            "recordedByID": contact_ids,
            "project_contact": contact_names,
            "institution": institutions,
            "institutionID": [],
            "project_name": None,
            "project_id": None,
        }
    ]
    apply_query_result(project_result, term_row_map, write_project, none_placeholder="")

    # --- Publications and data-management fields ---
    pubs = get_publications(datasetid)
    citations = [p.get("citation") for p in pubs if p.get("citation")]
    dois = [p.get("doi") for p in pubs if p.get("doi")]
    associated = [f"https://doi.org/{d}" for d in dois]

    datamgmt_result = [
        {
            "license": "http://creativecommons.org/licenses/by/4.0/legalcode",
            "bibliographicCitation": citations,
            "associated_resource": associated,
            "mod_date": ds.get("recdatecreated"),
        }
    ]
    apply_query_result(datamgmt_result, term_row_map, write_project, none_placeholder="")

    return workbook
