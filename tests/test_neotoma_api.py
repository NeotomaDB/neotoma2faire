"""Tests for neotoma2faire.api.client.

All tests mock ``requests.get`` so no network calls are made.
"""

import json
from unittest.mock import MagicMock, patch

import pytest

from neotoma2faire.api.client import (
    get_contact,
    get_dataset,
    get_downloads,
    get_publications,
    get_taxa_batch,
)


def _mock_response(payload: dict) -> MagicMock:
    """Return a mock requests.Response that returns *payload* from .json()."""
    mock = MagicMock()
    mock.json.return_value = payload
    mock.raise_for_status.return_value = None
    return mock


# ---------------------------------------------------------------------------
# get_downloads
# ---------------------------------------------------------------------------

class TestGetDownloads:
    _payload = {
        "status": "success",
        "data": [
            {
                "site": {
                    "siteid": 34,
                    "sitename": "Linton",
                    "altitude": 333,
                    "geography": json.dumps({"type": "Point", "coordinates": [-91.28, 43.15]}),
                    "geopolitical": ["United States", "Iowa"],
                    "collectionunit": {
                        "collectionunitid": 34,
                        "colldate": None,
                        "collectiondevice": None,
                        "notes": None,
                        "depositionalenvironment": "Unknown",
                        "dataset": {
                            "datasetid": 34,
                            "datasettype": "pollen surface sample",
                            "datasetpi": [],
                            "samples": [],
                        },
                    },
                }
            }
        ],
    }

    def test_returns_site_dict(self):
        with patch("neotoma2faire.api.client.requests.get", return_value=_mock_response(self._payload)):
            result = get_downloads(34)
        assert result["site"]["siteid"] == 34

    def test_raises_on_http_error(self):
        mock = MagicMock()
        mock.raise_for_status.side_effect = Exception("404")
        with patch("neotoma2faire.api.client.requests.get", return_value=mock):
            with pytest.raises(Exception, match="404"):
                get_downloads(34)


# ---------------------------------------------------------------------------
# get_taxa_batch
# ---------------------------------------------------------------------------

class TestGetTaxaBatch:
    _payload = {
        "data": [
            {"taxonid": 29, "taxonname": "Betula", "highertaxonid": 32627},
            {"taxonid": 49, "taxonname": "Celtis", "highertaxonid": 9115},
        ]
    }

    def test_returns_list(self):
        with patch("neotoma2faire.api.client.requests.get", return_value=_mock_response(self._payload)):
            result = get_taxa_batch([29, 49])
        assert isinstance(result, list)
        assert len(result) == 2

    def test_taxon_fields_present(self):
        with patch("neotoma2faire.api.client.requests.get", return_value=_mock_response(self._payload)):
            result = get_taxa_batch([29])
        assert result[0]["taxonname"] == "Betula"
        assert result[0]["highertaxonid"] == 32627

    def test_empty_ids_returns_empty(self):
        with patch("neotoma2faire.api.client.requests.get", return_value=_mock_response({"data": []})):
            result = get_taxa_batch([])
        assert result == []


# ---------------------------------------------------------------------------
# get_publications
# ---------------------------------------------------------------------------

class TestGetPublications:
    _payload = {
        "data": {
            "result": [
                {
                    "publication": {
                        "publicationid": 38,
                        "citation": "Davis, A.M. 1977. ...",
                        "doi": "10.1111/j.1467-8306.1977.tb01133.x",
                        "year": "1977",
                    }
                }
            ]
        }
    }

    def test_returns_list_of_dicts(self):
        with patch("neotoma2faire.api.client.requests.get", return_value=_mock_response(self._payload)):
            result = get_publications(34)
        assert isinstance(result, list)
        assert result[0]["doi"] == "10.1111/j.1467-8306.1977.tb01133.x"

    def test_empty_result(self):
        with patch("neotoma2faire.api.client.requests.get", return_value=_mock_response({"data": {"result": []}})):
            result = get_publications(34)
        assert result == []


# ---------------------------------------------------------------------------
# get_contact
# ---------------------------------------------------------------------------

class TestGetContact:
    _payload = {
        "data": [
            {
                "contactid": 28,
                "contactname": "Davis, Anthony M.",
                "address": "Department of Geography\r\nUniversity of Toronto\r\nToronto, ON",
            }
        ]
    }

    def test_returns_dict(self):
        with patch("neotoma2faire.api.client.requests.get", return_value=_mock_response(self._payload)):
            result = get_contact(28)
        assert result["contactname"] == "Davis, Anthony M."

    def test_missing_contact_returns_empty_dict(self):
        with patch("neotoma2faire.api.client.requests.get", return_value=_mock_response({"data": []})):
            result = get_contact(999)
        assert result == {}
