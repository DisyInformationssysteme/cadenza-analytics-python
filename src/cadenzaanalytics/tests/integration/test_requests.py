"""Incoming requests expose usable data, metadata, and client context."""

from zoneinfo import ZoneInfo
import re

import pandas as pd
import pytest
from shapely.geometry import Point

import cadenzaanalytics as ca

from .client import column


@pytest.mark.parametrize("part_style", ["files", "fields"])
def test_order_data_arrives_typed_and_ready_for_analysis(extension_client, orders_payload, part_style):
    def analyse(request):
        assert list(request) == ["orders"]
        assert len(request) == 1
        assert "orders" in request
        data = request["orders"].data
        assert data["order_id"].tolist() == [101, 102, 103]
        assert data.loc[0, "quantity"] == 2
        assert data.loc[0, "unit_price"] == 3.5
        assert data.loc[0, "product"] == "Kaffee aus München"
        assert data.loc[1, "product"] == "Tea; Earl Grey"
        assert data.loc[2, "product"] == ""
        assert data.loc[0, "purchased_at"] == pd.Timestamp("2026-01-15T09:30:00Z")
        assert data.loc[1, "purchased_at"] == pd.Timestamp("2026-07-15T08:30:00Z")
        assert data.loc[0, "location"] == Point(8.4, 49)
        assert data.loc[2, "location"] == Point(0, 0)
        for name in ("quantity", "unit_price", "purchased_at"):
            assert pd.isna(data.loc[2, name]), f"Missing {name} must stay missing"
        return ca.TextResponse("All order data is usable")

    response = extension_client(analyse).invoke(**orders_payload, part_style=part_style)

    assert response.status_code == 200
    assert response.text == "All order data is usable"


def test_column_metadata_can_be_looked_up_and_grouped(extension_client, orders_payload):
    def analyse(request):
        metadata = request["orders"].metadata
        assert len(metadata) == 6
        assert list(metadata) == ["order_id", "product", "quantity", "unit_price", "purchased_at", "location"]
        assert "quantity" in metadata
        assert "unknown" not in metadata
        assert [item.name for item in metadata.columns] == list(metadata)
        assert [item.name for item in metadata.groups["values"]] == [
            "product", "quantity", "unit_price", "purchased_at",
        ]
        assert metadata.id_names == ["order_id"]
        assert [item.name for item in metadata.ids] == ["order_id"]
        quantity = metadata["quantity"]
        assert quantity.print_name == "Quantity"
        assert quantity.data_type == ca.DataType.INT64
        assert quantity.role == ca.AttributeRole.MEASURE
        assert quantity.measure_aggregation == ca.MeasureAggregation.SUM
        assert metadata["unit_price"].format == "0.00"
        assert metadata["location"].geometry_type == ca.GeometryType.POINT
        assert metadata["location"].srs == "EPSG:4326"
        with pytest.raises(KeyError):
            _ = metadata["unknown"]
        with pytest.raises(KeyError):
            _ = request["unknown"]
        return ca.TextResponse("Metadata available")

    assert extension_client(analyse).invoke(**orders_payload).status_code == 200


@pytest.mark.parametrize("explicit_nulls", [False, True], ids=["omitted", "explicit-null"])
def test_optional_column_metadata_can_be_absent_or_null(extension_client, explicit_nulls):
    incoming = column("label")
    if explicit_nulls:
        incoming.update(role=None, measureAggregation=None, geometryType=None, format=None, srs=None)

    def analyse(request):
        metadata = request["orders"].metadata["label"]
        assert metadata.role is None
        assert metadata.measure_aggregation is None
        assert metadata.geometry_type is None
        assert metadata.format is None
        assert metadata.srs is None
        assert metadata.attribute_group_name == "values"
        return ca.DataResponse(request["orders"].data, request["orders"].metadata.columns)

    response = extension_client(analyse, extension_type=ca.ExtensionType.DATA).invoke(
        columns=[incoming], csv_data='"label"\r\n"example"\r\n',
    )

    assert response.status_code == 200
    assert response.rows == [["label"], ["example"]]
    assert response.container["columns"] == [column("label")]


def test_omitting_an_attribute_group_uses_the_default_group(extension_client):
    incoming = {"name": "label", "printName": "Label", "dataType": "string"}

    def analyse(request):
        metadata = request["orders"].metadata
        assert metadata["label"].attribute_group_name == "data"
        assert [item.name for item in metadata.groups["data"]] == ["label"]
        assert metadata.ids is None
        assert metadata.id_names is None
        return ca.TextResponse("Default group available")

    assert extension_client(analyse).invoke(columns=[incoming], csv_data='"label"\r\n"x"\r\n').status_code == 200


@pytest.mark.parametrize("part_style", ["files", "fields"])
def test_text_roundtrip_preserves_empty_missing_quotes_and_embedded_newlines(extension_client, part_style):
    csv_data = (
        '"label";"note"\r\n'
        '"";\r\n'
        ';""\r\n'
        '"Grüße; 世界";"He said ""hello""\r\non two lines"\r\n'
    )

    def echo(request):
        table = request["orders"]
        assert table.data.loc[0, "label"] == ""
        assert pd.isna(table.data.loc[0, "note"])
        assert pd.isna(table.data.loc[1, "label"])
        assert table.data.loc[1, "note"] == ""
        assert table.data.loc[2, "note"] == 'He said "hello"\r\non two lines'
        return ca.DataResponse(table.data, table.metadata.columns)

    response = extension_client(echo, extension_type=ca.ExtensionType.DATA).invoke(
        columns=[column("label"), column("note")], csv_data=csv_data, part_style=part_style,
    )

    assert response.status_code == 200
    assert response.text == csv_data


def test_header_only_table_is_available_even_without_rows(extension_client):
    def analyse(request):
        table = request["orders"]
        assert table.data.empty
        assert list(table.data.columns) == ["label"]
        assert table.metadata["label"].data_type == ca.DataType.STRING
        return ca.DataResponse(table.data, table.metadata.columns)

    response = extension_client(analyse, extension_type=ca.ExtensionType.DATA).invoke(
        columns=[column("label")], csv_data='"label"\r\n',
    )

    assert response.status_code == 200
    assert response.rows == [["label"]]


@pytest.mark.parametrize("containers", [None, [], [{"columns": []}]], ids=["null", "empty", "no-columns"])
def test_extension_can_run_without_input_tables(extension_client, containers):
    def generate(request):
        assert len(request) == 0
        assert not list(request)
        assert "orders" not in request
        return ca.DataResponse(pd.DataFrame({"result": [42]}), [])

    response = extension_client(generate, tables=[], extension_type=ca.ExtensionType.DATA).invoke(
        metadata={"dataContainers": containers, "parameters": []},
    )

    assert response.status_code == 200
    assert response.rows == [["result"], ["42"]]


def test_cadenza_version_and_timezone_headers_reach_extension_code(extension_client):
    def analyse(request):
        assert request.cadenza_version == "11.1.0"
        assert request.cadenza_timezone_region == "Europe/Berlin"
        assert request.cadenza_timezone_current_offset == "+02:00"
        return ca.TextResponse("Client context available")

    response = extension_client(analyse, tables=[]).invoke(headers={
        "X-Disy-Cadenza-Version": "11.1.0",
        "X-Disy-Cadenza-Timezone-Region": "Europe/Berlin",
        "X-Disy-Cadenza-Timezone-Current-Offset": "+02:00",
    })

    assert response.status_code == 200


def test_older_clients_without_context_headers_get_a_usable_local_timezone(extension_client):
    def analyse(request):
        assert request.cadenza_version is None
        assert ZoneInfo(request.cadenza_timezone_region) is not None
        assert re.fullmatch(r"[+-]\d{2}:\d{2}(:\d{2}(\.\d+)?)?", request.cadenza_timezone_current_offset)
        return ca.TextResponse("Local context available")

    assert extension_client(analyse, tables=[]).invoke().status_code == 200


def test_unknown_metadata_from_a_newer_client_does_not_break_existing_extensions(extension_client):
    def echo(request):
        table = request["orders"]
        return ca.DataResponse(table.data, table.metadata.columns)

    response = extension_client(echo, extension_type=ca.ExtensionType.DATA).invoke(metadata={
        "futureFeature": {"enabled": True},
        "dataContainers": [{"columns": [column("label", futureColumnSetting="new")]}],
        "parameters": [],
    }, csv_data='"label"\r\n"example"\r\n')

    assert response.status_code == 200
    assert response.container["columns"] == [column("label")]


@pytest.mark.filterwarnings("error:Invalid WKT")
def test_missing_geometry_values_reach_analytics_as_missing_values(extension_client):
    def analyse(request):
        data = request["orders"].data
        assert data.loc[0, "location"] == Point(8.4, 49)
        assert pd.isna(data.loc[1, "location"])
        return ca.TextResponse("Missing geometry accepted")

    response = extension_client(analyse).invoke(columns=[
        column("id", "int64"),
        column("location", "geometry", geometryType="point", srs="EPSG:4326"),
    ], csv_data='"id";"location"\r\n"1";"POINT (8.4 49)"\r\n"2";\r\n')

    assert response.status_code == 200


@pytest.mark.parametrize("wire_geometry", ['""', '"NOT_WKT"'], ids=["empty-string", "invalid-wkt"])
def test_invalid_geometry_text_warns_and_reaches_analytics_as_missing(extension_client, wire_geometry):
    def analyse(request):
        assert pd.isna(request["orders"].data.loc[0, "location"])
        return ca.TextResponse("Invalid geometry treated as missing")

    with pytest.warns(Warning, match="Invalid WKT"):
        response = extension_client(analyse).invoke(columns=[
            column("id", "int64"),
            column("location", "geometry", geometryType="point", srs="EPSG:4326"),
        ], csv_data=f'"id";"location"\r\n"1";{wire_geometry}\r\n')

    assert response.status_code == 200


@pytest.mark.filterwarnings("error:Invalid WKT")
def test_valid_empty_geometry_is_preserved_in_a_roundtrip(extension_client):
    def echo(request):
        table = request["orders"]
        geometry = table.data.loc[0, "location"]
        assert geometry.is_empty
        assert geometry.geom_type == "Point"
        return ca.DataResponse(table.data, table.metadata.columns)

    csv_data = '"id";"location"\r\n"1";"POINT EMPTY"\r\n'
    response = extension_client(echo, extension_type=ca.ExtensionType.DATA).invoke(columns=[
        column("id", "int64"),
        column("location", "geometry", geometryType="point", srs="EPSG:4326"),
    ], csv_data=csv_data)

    assert response.status_code == 200
    assert response.text == csv_data


@pytest.mark.parametrize("field", ["name", "printName", "dataType", "attributeGroupName"])
def test_null_required_column_metadata_is_rejected_before_analytics_runs(extension_client, field):
    incoming = column("label")
    incoming[field] = None

    def analyse(_request):
        pytest.fail("Invalid required metadata must be rejected before analytics runs")

    with pytest.raises(ValueError):
        extension_client(analyse).invoke(columns=[incoming], csv_data='"label"\r\n"example"\r\n')


@pytest.mark.parametrize("field,value", [
    ("dataType", "unknown"), ("role", "unknown"),
    ("measureAggregation", "unknown"), ("geometryType", "unknown"),
])
def test_invalid_column_enum_values_are_still_rejected(extension_client, field, value):
    incoming = column("label")
    incoming[field] = value

    def analyse(_request):
        pytest.fail("Invalid enum metadata must be rejected before analytics runs")

    with pytest.raises(ValueError):
        extension_client(analyse).invoke(columns=[incoming], csv_data='"label"\r\n"example"\r\n')
