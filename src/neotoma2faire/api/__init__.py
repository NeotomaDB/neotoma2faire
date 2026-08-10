"""HTTP client for Neotoma.

* :mod:`neotoma2faire.api.client` — REST API v2.0 wrappers (no auth needed).
"""
from .client import (
    get_aedna_sequences,
    get_assays_by_dataset,
    get_contact,
    get_dataset,
    get_downloads,
    get_projects_by_dataset,
    get_publications,
    get_site,
    get_taxa_batch,
)

__all__ = [
    "get_aedna_sequences",
    "get_assays_by_dataset",
    "get_contact",
    "get_dataset",
    "get_downloads",
    "get_projects_by_dataset",
    "get_publications",
    "get_site",
    "get_taxa_batch",
]
