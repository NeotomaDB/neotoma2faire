"""Tests for neotoma2faire.extract.data.

Covers the two private helpers and the public ``get_data`` entry point.

The download structure is built inline rather than read from
``tests/fixtures/downloads_*.json`` — those files are empty stubs (zero
samples) pending a live API refresh, so they cannot exercise the flattening
path. Building the nested dict here also keeps each assertion traceable to the
input that produced it.
"""

import json
from unittest.mock import patch

from neotoma2faire.extract.data import (
    _chronology_suffixes,
    _pick_chronology,
    _point_from_geometry,
    get_data,
)


class TestPointFromGeometry:
    def test_point(self):
        geo = {"type": "Point", "coordinates": [-75.06667, 55.41333]}
        assert _point_from_geometry(geo) == (-75.06667, 55.41333)

    def test_polygon_returns_centroid(self):
        # A closed bbox ring; centroid is the box centre, closing vertex ignored.
        geo = {
            "type": "Polygon",
            "coordinates": [
                [
                    [99.749, 31.0998],
                    [99.749, 31.122],
                    [99.759, 31.122],
                    [99.759, 31.0998],
                    [99.749, 31.0998],
                ]
            ],
        }
        lon, lat = _point_from_geometry(geo)
        assert round(lon, 4) == 99.754
        assert round(lat, 4) == 31.1109

    def test_empty_geometry(self):
        assert _point_from_geometry({}) == (None, None)

    def test_missing_coordinates(self):
        assert _point_from_geometry({"type": "Point"}) == (None, None)


def _chron(chronologyid, agemodel="CRS", modelagetype="Calendar years BP"):
    """One entry of a collection unit's ``chronologies`` list.

    The API nests the metadata one level deeper than the id, which is exactly
    what ``_pick_chronology`` has to flatten.
    """
    return {
        "chronology": {
            "chronologyid": chronologyid,
            "chronology": {"agemodel": agemodel, "modelagetype": modelagetype},
        }
    }


class TestPickChronology:
    def test_no_chronologies_returns_empty(self):
        assert _pick_chronology({}) == {}
        assert _pick_chronology({"chronologies": []}) == {}
        assert _pick_chronology({"chronologies": None}) == {}

    def test_single_chronology_is_used_without_a_default_flag(self):
        cu = {"chronologies": [_chron(11)]}
        assert _pick_chronology(cu) == {
            "chronologyid": 11,
            "agemodel": "CRS",
            "modelagetype": "Calendar years BP",
        }

    def test_default_chronology_wins(self):
        cu = {
            "defaultchronology": 22,
            "chronologies": [_chron(11, agemodel="CRS"), _chron(22, agemodel="CIC")],
        }
        assert _pick_chronology(cu)["chronologyid"] == 22
        assert _pick_chronology(cu)["agemodel"] == "CIC"

    def test_falls_back_to_first_when_default_is_absent_from_the_list(self):
        cu = {"defaultchronology": 99, "chronologies": [_chron(11), _chron(22)]}
        assert _pick_chronology(cu)["chronologyid"] == 11

    def test_entries_with_neither_id_nor_metadata_are_dropped(self):
        cu = {"chronologies": [{"chronology": {}}, _chron(11)]}
        assert _pick_chronology(cu)["chronologyid"] == 11

    def test_isdefault_flag_wins_when_the_unit_names_no_default(self):
        first, flagged = _chron(11), _chron(22)
        flagged["chronology"]["chronology"]["isdefault"] = True
        assert _pick_chronology({"chronologies": [first, flagged]})["chronologyid"] == 22

    def test_the_chronology_the_samples_cite_beats_the_first_one(self):
        # West Okoboji (74666) carries four chronologies, defaultchronology is
        # null and none is flagged isdefault -- but every sample age belongs to
        # the last of them.  Picking the first would leave `age` unset and the
        # ageModels sheet blank.
        cu = {"chronologies": [_chron(11), _chron(22), _chron(33)]}
        samples = [
            {"ages": [{"chronologyid": 33, "age": 100}]},
            {"ages": [{"chronologyid": 33, "age": 200}]},
            {"ages": [{"chronologyid": None, "age": None}]},
        ]
        assert _pick_chronology(cu, samples)["chronologyid"] == 33

    def test_an_explicit_default_still_beats_what_the_samples_cite(self):
        cu = {"defaultchronology": 11, "chronologies": [_chron(11), _chron(22)]}
        samples = [{"ages": [{"chronologyid": 22}]}]
        assert _pick_chronology(cu, samples)["chronologyid"] == 11

    def test_samples_citing_an_unknown_chronology_fall_back_to_the_first(self):
        cu = {"chronologies": [_chron(11), _chron(22)]}
        samples = [{"ages": [{"chronologyid": 999}]}]
        assert _pick_chronology(cu, samples)["chronologyid"] == 11


class TestChronologySuffixes:
    """Duplicate chronology names must not collapse into one set of columns."""

    def test_unique_names_are_used_as_is(self):
        records = [
            {"chronologyid": 11, "chronologyname": "Core top"},
            {"chronologyid": 22, "chronologyname": "Pb-210"},
        ]
        assert _chronology_suffixes(records) == {11: "Core_top", 22: "Pb-210"}

    def test_duplicate_names_are_disambiguated_by_id(self):
        # All four of West Okoboji's chronologies are named "DefaultChronology".
        records = [
            {"chronologyid": 11, "chronologyname": "DefaultChronology"},
            {"chronologyid": 22, "chronologyname": "DefaultChronology"},
        ]
        assert _chronology_suffixes(records) == {
            11: "DefaultChronology_11",
            22: "DefaultChronology_22",
        }

    def test_a_missing_name_falls_back_to_the_id(self):
        assert _chronology_suffixes([{"chronologyid": 11, "chronologyname": None}]) == {11: "11"}


def _sample(sampleid, samplename, depth, datums, ages=()):
    return {
        "sampleid": sampleid,
        "samplename": samplename,
        "analysisunitid": 1000 + sampleid,
        "analysisunitname": f"AU-{sampleid}",
        "depth": depth,
        "thickness": 1.0,
        "igsn": f"IGSN{sampleid}",
        "preparationmethod": "DNA extraction",
        "ages": list(ages),
        "datum": list(datums),
    }


def _datum(taxonid, value, taxongroup="Vascular plants", variablename=None):
    return {
        "taxonid": taxonid,
        "value": value,
        "variablename": variablename or f"taxon-{taxonid}",
        "units": "present/absent",
        "element": "DNA",
        "taxongroup": taxongroup,
        "ecologicalgroup": "TRSH",
    }


_DEFAULT = object()  # lets a test pass geography=None to mean "absent"


def _download(samples, geography=_DEFAULT, defaultchronology=22, chronologies=None):
    return {
        "site": {
            "siteid": 5001,
            "sitename": "Lake Okoboji",
            "geography": json.dumps({"type": "Point", "coordinates": [-95.15, 43.38]})
            if geography is _DEFAULT
            else geography,
            "altitude": 430,
            "geopolitical": ["United States", "Iowa"],
            "collectionunit": {
                "collectionunitid": 6001,
                "colldate": "2018-07-14",
                "collectiondevice": "Livingstone piston corer",
                "notes": "core WLO18",
                "depositionalenvironment": "Lacustrine",
                "defaultchronology": defaultchronology,
                "chronologies": chronologies
                if chronologies is not None
                else [_chron(22, agemodel="CRS")],
                "dataset": {
                    "datasetid": 74655,
                    "datasettype": "aeDNA",
                    "samples": samples,
                },
            },
        }
    }


def _run(download):
    with patch("neotoma2faire.extract.data.get_downloads", return_value=download):
        return get_data(74655)


class TestGetData:
    def test_one_row_per_sample_times_datum(self):
        download = _download(
            [
                _sample(1, "S1", 0.5, [_datum(101, 12), _datum(102, 3)]),
                _sample(2, "S2", 1.5, [_datum(101, 7)]),
            ]
        )
        df = _run(download)

        assert len(df) == 3
        assert list(df["samp_name"]) == ["S1", "S1", "S2"]
        assert list(df["taxonid"]) == [101, 102, 101]
        assert list(df["value"]) == [12, 3, 7]

    def test_no_samples_yields_empty_frame(self):
        assert _run(_download([])).empty

    def test_sample_with_no_datums_contributes_no_rows(self):
        assert _run(_download([_sample(1, "S1", 0.5, [])])).empty

    def test_site_columns_repeat_on_every_row(self):
        df = _run(_download([_sample(1, "S1", 0.5, [_datum(101, 1), _datum(102, 2)])]))

        assert set(df["sitename"]) == {"Lake Okoboji"}
        assert set(df["decimalLatitude"]) == {43.38}
        assert set(df["decimalLongitude"]) == {-95.15}
        assert set(df["elev"]) == {430}
        assert set(df["geo_loc_name"]) == {"United States, Iowa"}

    def test_faire_named_columns_are_present(self):
        df = _run(_download([_sample(1, "S1", 0.5, [_datum(101, 1)])]))

        for column in (
            "decimalLatitude",
            "decimalLongitude",
            "elev",
            "geo_loc_name",
            "eventDate",
            "verbatimEventDate",
            "samp_collect_device",
            "samp_collect_method",
            "env_medium",
            "samp_name",
            "sample_derived_from",
            "minimumDepthInMeters",
            "maximumDepthInMeters",
            "materialSampleID",
            "taxonid",
            "value",
        ):
            assert column in df.columns

    def test_collection_unit_fields_are_mapped(self):
        df = _run(_download([_sample(1, "S1", 0.5, [_datum(101, 1)])]))
        row = df.iloc[0]

        assert row["eventDate"] == "2018-07-14"
        assert row["verbatimEventDate"] == "2018-07-14"
        assert row["samp_collect_device"] == "Livingstone piston corer"
        assert row["samp_collect_method"] == "core WLO18"
        assert row["env_medium"] == "Lacustrine"
        assert row["samp_category"] == "sample"

    def test_depth_populates_both_faire_depth_columns(self):
        df = _run(_download([_sample(1, "S1", 0.5, [_datum(101, 1)])]))

        assert df.iloc[0]["minimumDepthInMeters"] == 0.5
        assert df.iloc[0]["maximumDepthInMeters"] == 0.5

    def test_default_chronology_maps_to_plain_age_columns(self):
        ages = [
            {
                "chronologyid": 22,
                "age": 150,
                "ageolder": 175,
                "ageyounger": 125,
                "agetype": "Calendar years BP",
            }
        ]
        df = _run(_download([_sample(1, "S1", 0.5, [_datum(101, 1)], ages=ages)]))
        row = df.iloc[0]

        assert row["age"] == 150
        assert row["ageOldest"] == 175
        assert row["ageYoungest"] == 125
        assert row["ageUnit"] == "Calendar years BP"

    def test_non_default_chronology_gets_suffixed_columns(self):
        ages = [
            {"chronologyid": 22, "age": 150, "agetype": "Calendar years BP"},
            {
                "chronologyid": 33,
                "chronologyname": "Pb 210 CIC",
                "age": 160,
                "ageolder": 180,
                "ageyounger": 140,
                "agetype": "Calendar years BP",
            },
        ]
        df = _run(_download([_sample(1, "S1", 0.5, [_datum(101, 1)], ages=ages)]))
        row = df.iloc[0]

        assert row["age"] == 150
        assert row["age_Pb_210_CIC"] == 160
        assert row["ageOldest_Pb_210_CIC"] == 180
        assert row["ageYoungest_Pb_210_CIC"] == 140

    def test_unnamed_extra_chronology_is_suffixed_with_its_id(self):
        ages = [
            {"chronologyid": 22, "age": 150},
            {"chronologyid": 33, "age": 160},
        ]
        df = _run(_download([_sample(1, "S1", 0.5, [_datum(101, 1)], ages=ages)]))

        assert df.iloc[0]["age_33"] == 160

    def test_age_entry_without_a_chronology_id_is_skipped(self):
        ages = [{"age": 150, "agetype": "Calendar years BP"}]
        df = _run(_download([_sample(1, "S1", 0.5, [_datum(101, 1)], ages=ages)]))

        assert "age" not in df.columns

    def test_chronology_metadata_is_copied_onto_every_row(self):
        df = _run(_download([_sample(1, "S1", 0.5, [_datum(101, 1)])]))

        assert df.iloc[0]["agemodel"] == "CRS"
        assert df.iloc[0]["modelagetype"] == "Calendar years BP"

    def test_missing_geography_leaves_coordinates_null(self):
        df = _run(_download([_sample(1, "S1", 0.5, [_datum(101, 1)])], geography=None))

        assert df.iloc[0]["decimalLatitude"] is None
        assert df.iloc[0]["decimalLongitude"] is None

    def test_lab_analyses_are_kept_and_tagged_by_taxongroup(self):
        """make_template filters these out; get_data must still return them."""
        download = _download(
            [
                _sample(
                    1,
                    "S1",
                    0.5,
                    [
                        _datum(101, 12),
                        _datum(999, 0.14, taxongroup="Laboratory analyses",
                               variablename="Sedimentation rate"),
                    ],
                )
            ]
        )
        df = _run(download)

        assert len(df) == 2
        assert set(df["taxongroup"]) == {"Vascular plants", "Laboratory analyses"}

    def test_duplicate_rows_are_dropped(self):
        duplicate = _datum(101, 12)
        df = _run(_download([_sample(1, "S1", 0.5, [duplicate, dict(duplicate)])]))

        assert len(df) == 1
        assert list(df.index) == [0]
