"""Populate the projectMetadata sheet with dataset provenance information.

Queries the Neotoma REST API v2.0 (no database credentials required) for the
project(s) linked to a dataset and their participants, then maps the results
onto the ``projectMetadata`` worksheet using the ``term_name`` → row mapping
already present in that sheet.

The ``projectMetadata`` sheet is a *vertical* metadata table: each FAIRe term
occupies its own *row* (``term_name`` in column C), and the populated value goes
in column D (``project_level``).

Project identity terms (``project_id``, ``recordedBy``, ``project_contact``)
come from ``ndb.projects``/``projectparticipants``.  The PCR/assay/sequencing
terms come from ``ndb.aednaassays`` (+ ``ndb.aednalibraries``) via the
``/datasets/{id}/assays`` endpoint; any term whose source value is absent is
left blank.
"""

from ..api.client import get_assays_by_dataset, get_dataset, get_projects_by_dataset
from ..utils import format_db_value

# FAIRe projectMetadata term ← ndb.aednaassays column.
_ASSAY_TERMS = {
    "assay_type": "assaytype",
    "assay_name": "assayname",
    "targetTaxonomicAssay": "targettaxonomicassay",
    "target_gene": "targetgene",
    "ampliconSize": "ampliconsize",
    "pcr_primer_forward": "pcrprimerforward",
    "pcr_primer_reverse": "pcrprimerreverse",
    "pcr_primer_reference_forward": "pcrprimerreferenceforward",
    "pcr_primer_reference_reverse": "pcrprimerreferencereverse",
    "probeReporter": "probereporter",
    "probeQuencher": "probequencher",
    "probe_seq": "probeseq",
    "probe_ref": "proberef",
    "probe_conc": "probeconc",
    "sterilise_method": "sterilisemethod",
}

# FAIRe projectMetadata term ← ndb.aednaassays BOOLEAN column.  Written as
# "0"/"1" to match the checklist's Boolean vocabulary (see the template's
# Drop-down values sheet).  NULL leaves the cell blank rather than becoming
# "0", because "unknown" and "no controls were used" are different claims.
_ASSAY_BOOLEAN_TERMS = {
    "neg_cont_0_1": "negcont",
    "pos_cont_0_1": "poscont",
}

# Assay types that involve an amplification step, used to derive pcr_0_1.
_AMPLIFICATION_ASSAY_TYPES = {"metabarcoding", "qpcr", "ddpcr", "pcr"}


# FAIRe projectMetadata term ← ndb.aednalibraries column.
_LIBRARY_TERMS = {
    "barcoding_pcr_appr": "barcodingpcrappr",
    "platform": "platform",
    "instrument": "instrument",
    "seq_kit": "seqkit",
    "lib_screen": "libscreen",
}


def _boolean_flag(value):
    """Normalise a FAIRe Boolean term to ``"1"``, ``"0"`` or ``None``.

    Accepts what the API might return for a Postgres ``BOOLEAN`` now or later:
    ``True``/``False``, ``1``/``0``, and the strings ``"true"``/``"false"``.
    ``None`` (SQL NULL) stays ``None`` so the caller leaves the cell empty.
    """
    if value is None:
        return None
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in ("true", "1", "yes"):
            return "1"
        if lowered in ("false", "0", "no"):
            return "0"
        return None
    return "1" if value else "0"


def _pcr_performed(assay: dict):
    """Derive ``pcr_0_1`` from the assay record.

    Neotoma stores no "was PCR run" flag, but it does not need one: an
    amplification-based assay type, or a PCR primer on record, means the step
    happened.  Returns ``None`` when neither is present, so an assay that says
    nothing about PCR leaves the cell blank instead of asserting ``"0"``.
    """
    assay_type = (assay.get("assaytype") or "").strip().lower()
    has_primer = bool(assay.get("pcrprimerforward") or assay.get("pcrprimerreverse"))
    if assay_type in _AMPLIFICATION_ASSAY_TYPES or has_primer:
        return "1"
    return None


def add_project(workbook, datasetid: int, checklist_version: str | None = None):
    """Write project metadata for *datasetid* into the workbook.

    Reads the ``term_name`` column of the ``projectMetadata`` sheet to build a
    row-index lookup, then calls ``GET /datasets/{id}/projects`` to fill
    ``project_id``, ``recordedBy``, and ``project_contact``.  When no project is
    linked, falls back to the dataset PI list so ``recordedBy`` is still filled.

    Args:
        workbook (openpyxl.Workbook): Workbook whose ``projectMetadata`` sheet
            will be populated.
        datasetid (int): Neotoma dataset ID whose provenance should be written.
        checklist_version (str | None): FAIRe checklist version the workbook was
            built from, written to ``checkls_ver``.  Derive it from the template
            filename with :func:`~.utils.checklist_version`.  Defaults to
            ``None``, which leaves that cell blank.

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

    # The FAIRe checklist version the workbook was built from.
    set_term("checkls_ver", checklist_version)

    # Assay / PCR / sequencing terms from ndb.aednaassays + ndb.aednalibraries.
    assays = get_assays_by_dataset(datasetid)
    if assays:
        assay = assays[0]
        for term, key in _ASSAY_TERMS.items():
            set_term(term, assay.get(key))
        for term, key in _ASSAY_BOOLEAN_TERMS.items():
            set_term(term, _boolean_flag(assay.get(key)))
        set_term("pcr_0_1", _pcr_performed(assay))
        libraries = assay.get("libraries") or []
        library = libraries[0] if libraries else {}
        for term, key in _LIBRARY_TERMS.items():
            set_term(term, library.get(key))

    return workbook
