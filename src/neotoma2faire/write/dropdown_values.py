"""Populate the Drop-down values sheet with controlled vocabulary terms.

The FAIRe template ships with a ``Drop-down values`` worksheet that lists the
valid choices for enumerated fields used across all other sheets.  This module
populates that sheet from the imagined Neotoma controlled-vocabulary tables
that will hold the FAIRe vocabulary once the schema extension is deployed:

* ``ndb.assaytypes`` → column ``assay_type``
* ``ndb.negativecontroltypes`` → column ``neg_cont_type``
* ``ndb.samplecategories`` → column ``samp_category``
* ``ndb.samplestoragesolutions`` → column ``samp_store_sol``
* ``ndb.spatialreferencesystems`` → column ``verbatimSRS``

Each vocabulary is written as a vertical list of values starting at row 2
under the matching column header in row 1.  Columns whose header is not
present in the sheet are silently skipped, so the function degrades gracefully
if the template version differs from the expected layout.
"""

#from ..api.db import neo_connect

# Maps FAIRe column header in the sheet to the SQL that fetches its vocabulary.
_VOCAB_QUERIES: dict[str, str] = {
    "assay_type": "SELECT assaytype FROM ndb.assaytypes ORDER BY assaytypeid",
    "neg_cont_type": (
        "SELECT negativecontroltype FROM ndb.negativecontroltypes ORDER BY negativecontroltypeid"
    ),
    "samp_category": (
        "SELECT samplecategory FROM ndb.samplecategories ORDER BY samplecategoryid"
    ),
    "samp_store_sol": (
        "SELECT samplestoragesolution FROM ndb.samplestoragesolutions ORDER BY samplestoragesolutionid"
    ),
    "verbatimSRS": (
        "SELECT spatialreferencesystem FROM ndb.spatialreferencesystems ORDER BY spatialreferencesystemid"
    ),
}


def add_dropdown_values(wb):
    """Write controlled vocabulary terms to the Drop-down values sheet.

    Reads the column-header row (row 1) of ``wb["Drop-down values"]`` to
    determine which vocabulary columns are present, then queries each imagined
    vocabulary table and writes the returned terms as a vertical list starting
    at row 2.

    Columns whose header does not match any key in :data:`_VOCAB_QUERIES` are
    left unchanged.  If a vocabulary table is empty or does not yet exist in
    the database the corresponding column is left blank.

    Args:
        wb (openpyxl.Workbook): Target workbook containing a
            ``Drop-down values`` sheet.

    Returns:
        openpyxl.Workbook: The same workbook with the ``Drop-down values``
        sheet updated.
    """
    ws = wb["Drop-down values"]

    # Build a mapping from column-header text → 1-based column index.
    header_map = {
        cell.value: cell.column
        for cell in ws[1]
        if cell.value is not None
    }

    conn = neo_connect()
    for col_name, query in _VOCAB_QUERIES.items():
        if col_name not in header_map:
            continue
        col_idx = header_map[col_name]
        try:
            with conn.cursor() as cur:
                cur.execute(query)
                rows = cur.fetchall()
        except Exception:  # noqa: BLE001 — imagined table may not exist yet
            continue
        for row_offset, row in enumerate(rows, start=2):
            value = next(iter(row.values()), None)
            ws.cell(row=row_offset, column=col_idx, value=value)

    return wb
