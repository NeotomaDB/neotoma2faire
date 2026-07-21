"""Fetch and assemble a Neotoma dataset into a single flat DataFrame.

Uses the Neotoma REST API v2.0 via :mod:`neotoma_api`

The public entry point is :func:`get_data`, which retrieves the full nested
site / collection-unit / sample / datum structure for a dataset ID and
flattens it into one tidy DataFrame ready for downstream processing.
"""

import json

import pandas as pd

from ..api.client import get_downloads


def _point_from_geometry(geo: dict) -> tuple[float | None, float | None]:
    """Return a representative ``(lon, lat)`` for any GeoJSON geometry.

    A ``Point`` yields its own coordinate; any nested geometry (``Polygon``,
    ``MultiPoint``, …) yields the centroid of every coordinate pair found, so
    sites recorded as bounding boxes still export a usable location instead of
    crashing.  Returns ``(None, None)`` when no coordinate pair is present.
    """
    pairs: list[tuple[float, float]] = []

    def walk(node):
        if (isinstance(node, (list, tuple)) and len(node) >= 2
                and all(isinstance(n, (int, float)) for n in node[:2])):
            pairs.append((node[0], node[1]))
        elif isinstance(node, (list, tuple)):
            for child in node:
                walk(child)

    walk(geo.get("coordinates"))
    if not pairs:
        return None, None
    uniq = list(dict.fromkeys(pairs))  # drop the repeated closing vertex of rings
    lon = sum(p[0] for p in uniq) / len(uniq)
    lat = sum(p[1] for p in uniq) / len(uniq)
    return lon, lat


def get_data(dsid: int) -> pd.DataFrame:
    """Download a Neotoma dataset and return a merged, cleaned DataFrame.

    Calls the Neotoma ``/v2.0/data/downloads/{dsid}`` endpoint and flattens
    the nested response into one row per (sample × taxon) combination.  All
    site, collection-unit, and sample metadata columns are repeated on every
    row so that downstream code can filter or deduplicate as needed.

    Columns mapped to FAIRe ``sampleMetadata`` names where a direct
    correspondence exists:

    ========================  ============================================
    Output column             Source field
    ========================  ============================================
    ``decimalLatitude``       site geography coordinates[1]
    ``decimalLongitude``      site geography coordinates[0]
    ``elev``                  site altitude
    ``geo_loc_name``          site geopolitical unit names (joined)
    ``eventDate``             collectionunit colldate
    ``verbatimEventDate``     collectionunit colldate
    ``samp_collect_device``   collectionunit collectiondevice
    ``samp_collect_method``   collectionunit notes
    ``env_medium``            collectionunit depositionalenvironment
    ``samp_name``             sample samplename
    ``sample_derived_from``   sample analysisunitid
    ``minimumDepthInMeters``  sample depth
    ``maximumDepthInMeters``  sample depth
    ``materialSampleID``      sample igsn
    ``taxonid``               datum taxonid
    ``value``                 datum value
    ========================  ============================================

    Args:
        dsid (int): Neotoma dataset ID to download.

    Returns:
        pandas.DataFrame: One row per sample × taxon combination, with all
        site, collection-unit, sample, and datum metadata columns.
    """
    dl = get_downloads(dsid)
    site = dl["site"]
    cu = site["collectionunit"]
    dataset = cu["dataset"]
    samples = dataset.get("samples", [])

    # Parse GeoJSON geography string (Point, Polygon bbox, etc.)
    geo = json.loads(site["geography"]) if site.get("geography") else {}
    lon, lat = _point_from_geometry(geo)
    geo_str = ", ".join(site.get("geopolitical") or [])

    default_chron_id = cu.get("defaultchronology")

    rows = []
    for sample in samples:
        base: dict = {
            # site
            "siteid": site.get("siteid"),
            "sitename": site.get("sitename"),
            "decimalLatitude": lat,
            "decimalLongitude": lon,
            "elev": site.get("altitude"),
            "geo_loc_name": geo_str or None,
            # collection unit
            "collectionunitid": cu.get("collectionunitid"),
            "eventDate": cu.get("colldate"),
            "verbatimEventDate": cu.get("colldate"),
            "samp_collect_device": cu.get("collectiondevice"),
            "samp_collect_method": cu.get("notes"),
            "env_medium": cu.get("depositionalenvironment"),
            # dataset
            "datasetid": dataset.get("datasetid"),
            "datasettype": dataset.get("datasettype"),
            # sample
            "sampleid": sample.get("sampleid"),
            "samp_name": sample.get("samplename"),
            "analysisunitid": sample.get("analysisunitid"),
            "sample_derived_from": sample.get("analysisunitid"),
            "minimumDepthInMeters": sample.get("depth"),
            "maximumDepthInMeters": sample.get("depth"),
            "materialSampleID": sample.get("igsn"),
            "samp_mat_process": sample.get("preparationmethod"),
            "samp_category": "sample",
        }

        # Ages — one entry per chronology in the API response.
        # The default chronology maps to the standard FAIRe age columns.
        # Each additional chronology gets suffixed columns so no data is lost.
        for age_entry in sample.get("ages", []):
            chron_id = age_entry.get("chronologyid")
            if chron_id is None:
                continue
            if chron_id == default_chron_id:
                base["age"] = age_entry.get("age")
                base["ageOldest"] = age_entry.get("ageolder")
                base["ageYoungest"] = age_entry.get("ageyounger")
                base["ageUnit"] = age_entry.get("agetype")
            else:
                raw = age_entry.get("chronologyname") or str(chron_id)
                suffix = raw.replace(" ", "_").replace("/", "_").replace("\\", "_")
                base[f"age_{suffix}"] = age_entry.get("age")
                base[f"ageOldest_{suffix}"] = age_entry.get("ageolder")
                base[f"ageYoungest_{suffix}"] = age_entry.get("ageyounger")
                base[f"ageUnit_{suffix}"] = age_entry.get("agetype")

        for datum in sample.get("datum", []):
            row = dict(base)
            row["taxonid"] = datum.get("taxonid")
            row["value"] = datum.get("value")
            row["variablename"] = datum.get("variablename")
            row["units"] = datum.get("units")
            row["element"] = datum.get("element")
            row["taxongroup"] = datum.get("taxongroup")
            row["ecologicalgroup"] = datum.get("ecologicalgroup")
            rows.append(row)

    return pd.DataFrame(rows).drop_duplicates().reset_index(drop=True)
