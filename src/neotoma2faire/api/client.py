"""Wrapper around the Neotoma REST API v2.0.

All functions call public, unauthenticated endpoints and return plain Python
dicts or lists.

Choosing an environment
-----------------------
Two Neotoma REST environments exist:

* ``prod`` (default) — ``https://api.neotomadb.org/v2.0/data``
* ``dev``            — ``https://api-dev.neotomadb.org/v2.0/data``

The base URL is selected at import time from the ``NEOTOMA_API_ENV``
environment variable.  Set it to ``"dev"`` to hit the development endpoints
(useful for testing new endpoints that haven't shipped to production yet);
anything else, or unset, picks production.

Examples::

    uv run neotoma2faire --dev template -d 74029 -o out.xlsx
    uv run neotoma2faire template -d 24 -o out.xlsx           # uses prod
"""

import os

import requests

_ENVIRONMENTS = {
    "prod":  "https://api.neotomadb.org/v2.0/data",
    "dev":   "https://api-dev.neotomadb.org/v2.0/data",
    "local": "http://localhost:3005/v2.0/data",
}

#: Active base URL — determined once at import time from ``NEOTOMA_API_ENV``.
#: Override at runtime by reassigning this attribute (the per-function
#: ``f"{BASE}/..."`` calls re-read it on every request).
BASE = _ENVIRONMENTS.get(os.environ.get("NEOTOMA_API_ENV", "prod"), _ENVIRONMENTS["prod"])


def use_environment(env: str) -> str:
    """Switch the active Neotoma API base URL at runtime.

    Args:
        env (str): ``"prod"`` or ``"dev"``.

    Returns:
        str: The newly active base URL.

    Raises:
        ValueError: If *env* is not a known environment name.
    """
    global BASE
    if env not in _ENVIRONMENTS:
        raise ValueError(f"unknown env {env!r}; choose from {list(_ENVIRONMENTS)}")
    BASE = _ENVIRONMENTS[env]
    return BASE


def _get(url: str, params: dict | None = None) -> dict:
    """GET a Neotoma API endpoint and return the parsed JSON body.

    Args:
        url (str): Full URL to request.
        params (dict | None): Optional query-string parameters.

    Returns:
        dict: Parsed JSON response.

    Raises:
        requests.HTTPError: If the server returns a non-2xx status code.
    """
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def get_downloads(datasetid: int) -> dict:
    """GET /v2.0/data/downloads/{datasetid}.

    Returns the full nested site → collectionunit → dataset → samples structure
    for one dataset.  This is the primary data source for :func:`get_data`.

    Args:
        datasetid (int): Neotoma dataset ID.

    Returns:
        dict: The first element of ``data[]`` from the API response, containing
        keys ``site`` (with nested ``collectionunit`` → ``dataset`` → ``samples``).
    """
    body = _get(f"{BASE}/downloads/{datasetid}")
    return body["data"][0]


def get_site(siteid: int) -> dict:
    """GET /v2.0/data/sites/{siteid}.

    Args:
        siteid (int): Neotoma site ID.

    Returns:
        dict: The ``site`` dict from the first result, containing ``siteid``,
        ``sitename``, ``geography``, ``altitude``, ``geopolitical``, etc.
    """
    body = _get(f"{BASE}/sites/{siteid}")
    return body["data"][0]["site"]


def get_taxa_batch(taxon_ids: list[int]) -> list[dict]:
    """GET /v2.0/data/taxa for a list of taxon IDs.

    Batches the IDs to keep URL length manageable (≤ 200 IDs per request).
    Each returned dict has at minimum ``taxonid``, ``taxonname``, and
    ``highertaxonid``.

    Args:
        taxon_ids (list[int]): Neotoma taxon IDs to look up.

    Returns:
        list[dict]: One dict per taxon in the same order as the API returns them.
    """
    results: list[dict] = []
    batch_size = 200
    for i in range(0, len(taxon_ids), batch_size):
        batch = taxon_ids[i : i + batch_size]
        ids_str = ",".join(map(str, batch))
        body = _get(f"{BASE}/taxa", params={"taxonid": ids_str})
        results.extend(body.get("data", []))
    return results


def get_publications(datasetid: int) -> list[dict]:
    """GET /v2.0/data/publications?datasetid={datasetid}.

    Args:
        datasetid (int): Neotoma dataset ID.

    Returns:
        list[dict]: One publication dict per result (keys: ``publicationid``,
        ``citation``, ``doi``, ``year``, ``author``, etc.).
    """
    body = _get(f"{BASE}/publications", params={"datasetid": datasetid})
    return [item["publication"] for item in body.get("data", {}).get("result", [])]


def get_dataset(datasetid: int) -> dict:
    """GET /v2.0/data/datasets/{datasetid}.

    Returns the ``site`` dict from the datasets endpoint, which includes a
    ``datasets`` list with PI contacts, dataset type, DOIs, and timestamps.

    Args:
        datasetid (int): Neotoma dataset ID.

    Returns:
        dict: The ``site`` dict from the first result.
    """
    body = _get(f"{BASE}/datasets/{datasetid}")
    return body["data"][0]["site"]


def _get_optional(url: str, key: str) -> list[dict]:
    """GET an endpoint that a given host may not serve, degrading to ``[]``.

    Several endpoints exist on some Neotoma hosts and not others, because the
    data has landed in the database ahead of the route.  A host that has not
    shipped one answers either with an HTTP error or — less helpfully — with an
    HTML error page under a 200, so both a failed status and an unparseable
    body mean "not available here".  Returning ``[]`` keeps the export running:
    a dataset with nothing to report simply leaves those sheets blank.

    Args:
        url (str): Full URL to request.
        key (str): Key to read out of the response's ``data`` object.

    Returns:
        list[dict]: The requested list, or ``[]`` when unavailable.
    """
    try:
        body = _get(url)
    except (requests.HTTPError, ValueError):
        return []
    return (body.get("data") or {}).get(key, [])


def get_projects_by_dataset(datasetid: int) -> list[dict]:
    """GET /v2.0/data/datasets/{datasetid}/projects.

    Returns the projects linked to a dataset, each with a ``participants`` list
    (``contactid``, ``contactname``, ``email``).

    Args:
        datasetid (int): Neotoma dataset ID.

    Returns:
        list[dict]: One dict per project, or ``[]`` when none / unavailable.
    """
    return _get_optional(f"{BASE}/datasets/{datasetid}/projects", "projects")


def get_assays_by_dataset(datasetid: int) -> list[dict]:
    """GET /v2.0/data/datasets/{datasetid}/assays.

    Returns the aeDNA assays linked to a dataset, each with a ``libraries`` list
    and an ``assaytype`` label.  Assay fields (``assayname``, ``targetgene``,
    ``pcrprimerforward``/``reverse``, …) feed the FAIRe ``projectMetadata`` PCR
    block; library fields (``platform``, ``instrument``, ``libid``, …) feed
    ``projectMetadata`` sequencing terms and ``experimentRunMetadata``.

    Args:
        datasetid (int): Neotoma dataset ID.

    Returns:
        list[dict]: One dict per assay, or ``[]`` when none / unavailable.
    """
    return _get_optional(f"{BASE}/datasets/{datasetid}/assays", "assays")


def get_aedna_sequences(datasetid: int) -> list[dict]:
    """GET /v2.0/data/aedna/sequences/{datasetid}.

    Returns the DNA sequences recorded for a dataset, grouped by taxon.  Each
    entry has ``taxonid``, ``taxonname``, ``taxonchain`` and a ``sequences``
    list whose members carry ``sequenceid``, ``sequence``, ``asv``, ``model``,
    ``primername`` and ``publicationdoi``.

    Named for the endpoint rather than the sheet: the tidy-DataFrame view used
    by the writers lives in
    :func:`~.extract.taxa_sequences.get_taxa_sequences`, which calls this.

    The sequence and ASV are what keep same-named taxa apart in the FAIRe
    ``finalReads`` sheet: two taxa can share a name — and even an ASV label —
    while differing only by their DNA sequence.

    Args:
        datasetid (int): Neotoma dataset ID.

    Returns:
        list[dict]: One dict per taxon, or ``[]`` when none / unavailable.
    """
    return _get_optional(f"{BASE}/aedna/sequences/{datasetid}", "sequences")


def get_contact(contactid: int) -> dict:
    """GET /v2.0/data/contacts/{contactid}.

    Args:
        contactid (int): Neotoma contact ID.

    Returns:
        dict: Contact record with ``contactname``, ``address``, ``email``, etc.
        Returns an empty dict if no contact is found.
    """
    body = _get(f"{BASE}/contacts/{contactid}")
    items = body.get("data", [])
    return items[0] if items else {}
