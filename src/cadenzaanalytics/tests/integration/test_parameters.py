"""Parameters arrive with useful Python values and optional metadata intact."""

from datetime import datetime

import pytest
from shapely.geometry import Point

import cadenzaanalytics as ca

from .client import parameter


@pytest.mark.parametrize("data_type,wire_value,expected", [
    ("string", "Grüße 世界", "Grüße 世界"),
    ("string", "", ""),
    ("string", "accurate", "accurate"),
    # Cadenza sends BOOLEAN parameters with dataType=string and a JSON boolean.
    ("string", False, False),
    ("string", True, True),
    ("int64", "9223372036854775807", 9223372036854775807),
    ("int64", 0, 0),
    ("int64", -12, -12),
    ("float64", "12.75", 12.75),
    ("float64", 0.0, 0.0),
    ("zonedDateTime", "2026-07-15T10:30:00+02:00", datetime.fromisoformat("2026-07-15T10:30:00+02:00")),
    ("geometry", "POINT (8.4 49)", Point(8.4, 49)),
], ids=["unicode", "empty", "selection", "false", "true", "large-integer", "zero", "negative",
        "decimal", "zero-decimal", "zoned-datetime", "geometry"])
def test_parameter_values_are_ready_to_use(extension_client, data_type, wire_value, expected):
    def analyse(request):
        assert request.parameters["input"] == expected
        assert isinstance(request.parameters["input"], type(expected))
        assert len(request.parameters) == 1
        assert list(request.parameters) == ["input"]
        assert "input" in request.parameters
        assert request.parameters.info("input").value == expected
        assert str(request.parameters.info("input").data_type) == data_type
        return ca.TextResponse("Parameter usable")

    response = extension_client(analyse, tables=[]).invoke(parameters=[parameter("input", data_type, wire_value)])

    assert response.status_code == 200
    assert response.text == "Parameter usable"


@pytest.mark.parametrize("data_type", ["string", "int64", "float64", "zonedDateTime", "geometry"])
@pytest.mark.parametrize("explicit_null_geometry", [False, True], ids=["omitted-enum", "null-enum"])
def test_null_parameter_values_stay_null_for_every_data_type(extension_client, data_type, explicit_null_geometry):
    incoming = parameter("optional", data_type, None, srs=None)
    if explicit_null_geometry:
        incoming["geometryType"] = None

    def analyse(request):
        assert "optional" in request.parameters
        assert request.parameters["optional"] is None
        info = request.parameters.info("optional")
        assert info.name == "optional"
        assert info.print_name == "optional"
        assert str(info.data_type) == data_type
        assert info.geometry_type is None
        assert info.srs is None
        return ca.TextResponse("Null retained")

    assert extension_client(analyse, tables=[]).invoke(parameters=[incoming]).status_code == 200


def test_omitted_parameter_differs_from_a_parameter_with_a_null_value(extension_client):
    def analyse(request):
        assert "optional" not in request.parameters
        assert request.parameters.get("optional", "fallback") == "fallback"
        assert request.parameters.info("optional") is None
        with pytest.raises(KeyError):
            _ = request.parameters["optional"]
        assert "explicit_null" in request.parameters
        assert request.parameters.get("explicit_null", "fallback") is None
        return ca.TextResponse("Absence and null remain distinct")

    response = extension_client(analyse, tables=[]).invoke(parameters=[parameter("explicit_null", "string", None)])

    assert response.status_code == 200


def test_geometry_parameter_includes_geometry_metadata(extension_client):
    def analyse(request):
        info = request.parameters.info("location")
        assert info.print_name == "Delivery location"
        assert info.geometry_type == ca.GeometryType.POINT
        assert info.srs == "EPSG:4326"
        assert request.parameters["location"] == Point(8.4, 49)
        return ca.TextResponse("Geometry metadata available")

    response = extension_client(analyse, tables=[]).invoke(parameters=[parameter(
        "location", "geometry", "POINT (8.4 49)", printName="Delivery location", geometryType="point", srs="EPSG:4326",
    )])

    assert response.status_code == 200


@pytest.mark.parametrize("provided", [False, True], ids=["no-view-size", "view-size-provided"])
def test_visual_extensions_can_read_view_dimensions(extension_client, provided):
    parameters = [
        parameter("net.disy.cadenza.imageWidth", "int64", 800),
        parameter("net.disy.cadenza.imageHeight", "int64", 600),
        parameter("net.disy.cadenza.devicePixelRatio", "float64", 2),
    ] if provided else []

    def visualise(request):
        view = request.parameters.view
        assert view.width == (800 if provided else None)
        assert view.height == (600 if provided else None)
        assert view.device_pixel_ratio == (2.0 if provided else None)
        return ca.TextResponse("View dimensions available")

    assert extension_client(visualise, tables=[], extension_type=ca.ExtensionType.VISUAL).invoke(
        parameters=parameters,
    ).status_code == 200


@pytest.mark.parametrize("field", ["name", "printName", "dataType"])
def test_null_required_parameter_metadata_is_rejected(extension_client, field):
    incoming = parameter("input", "string", "example")
    incoming[field] = None

    def analyse(_request):
        pytest.fail("Invalid parameter metadata must be rejected before analytics runs")

    with pytest.raises(ValueError):
        extension_client(analyse, tables=[]).invoke(parameters=[incoming])


@pytest.mark.parametrize("field", ["dataType", "geometryType"])
def test_unknown_parameter_enum_values_are_rejected(extension_client, field):
    incoming = parameter("input", "string", "example")
    incoming[field] = "unknown"

    def analyse(_request):
        pytest.fail("Invalid parameter metadata must be rejected before analytics runs")

    with pytest.raises(ValueError):
        extension_client(analyse, tables=[]).invoke(parameters=[incoming])
