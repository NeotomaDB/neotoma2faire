"""Tests for neotoma2faire.extract.data geometry parsing."""

from neotoma2faire.extract.data import _point_from_geometry


class TestPointFromGeometry:
    def test_point(self):
        geo = {"type": "Point", "coordinates": [-75.06667, 55.41333]}
        assert _point_from_geometry(geo) == (-75.06667, 55.41333)

    def test_polygon_returns_centroid(self):
        # A closed bbox ring; centroid is the box centre, closing vertex ignored.
        geo = {"type": "Polygon", "coordinates": [[
            [99.749, 31.0998], [99.749, 31.122],
            [99.759, 31.122], [99.759, 31.0998], [99.749, 31.0998],
        ]]}
        lon, lat = _point_from_geometry(geo)
        assert round(lon, 4) == 99.754
        assert round(lat, 4) == 31.1109

    def test_empty_geometry(self):
        assert _point_from_geometry({}) == (None, None)

    def test_missing_coordinates(self):
        assert _point_from_geometry({"type": "Point"}) == (None, None)
