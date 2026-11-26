"""An independent client can consume extension results and business errors."""

from base64 import b64decode

import pandas as pd
import pytest
from shapely.geometry import Point

import cadenzaanalytics as ca

from .client import column, parameter


def test_client_receives_a_calculated_result_from_typed_inputs_and_parameters(extension_client, orders_payload):
    def calculate(request):
        orders = request["orders"].data
        result = orders[["order_id"]].copy()
        result["total"] = (orders["quantity"] * orders["unit_price"] * request.parameters["factor"]).round(2)
        return ca.DataResponse(result, [
            ca.ColumnMetadata(name="order_id", print_name="Order ID", data_type=ca.DataType.INT64,
                              role=ca.AttributeRole.DIMENSION),
            ca.ColumnMetadata(name="total", print_name="Total", data_type=ca.DataType.FLOAT64,
                              role=ca.AttributeRole.MEASURE, measure_aggregation=ca.MeasureAggregation.SUM,
                              format="0.00"),
        ])

    orders_payload["metadata"]["parameters"] = [parameter("factor", "float64", "1.05")]
    response = extension_client(calculate, extension_type=ca.ExtensionType.DATA, parameters=[
        ca.Parameter(name="factor", print_name="Price factor", parameter_type=ca.ParameterType.FLOAT64),
    ]).invoke(**orders_payload)

    assert response.status_code == 200
    assert set(response.parts) == {"metadata", "response-data"}
    assert response.rows == [["order_id", "total"], ["101", "7.35"], ["102", "4.46"], ["103", "NaN"]]
    assert response.container == {
        "name": "response-data", "type": "text/csv",
        "columns": [
            column("order_id", "int64", printName="Order ID", attributeGroupName="data", role="dimension"),
            column("total", "float64", printName="Total", attributeGroupName="data", role="measure",
                   measureAggregation="sum", format="0.00"),
        ],
    }


def test_echo_response_preserves_metadata_and_serializes_typed_values(extension_client, orders_payload):
    def echo(request):
        table = request["orders"]
        return ca.DataResponse(table.data, table.metadata.columns)

    response = extension_client(echo, extension_type=ca.ExtensionType.DATA).invoke(**orders_payload)

    assert response.status_code == 200
    assert response.container["columns"] == orders_payload["metadata"]["dataContainers"][0]["columns"]
    assert response.rows == [
        ["order_id", "product", "quantity", "unit_price", "purchased_at", "location"],
        ["101", "Kaffee aus München", "2", "3.5", "2026-01-15T09:30:00Z", "POINT (8.4 49)"],
        ["102", "Tea; Earl Grey", "1", "4.25", "2026-07-15T08:30:00Z", "POINT (13.4 52.5)"],
        ["103", "", "", "NaN", "", "POINT (0 0)"],
    ]
    assert response.text.endswith('"103";"";;"NaN";;"POINT (0 0)"\r\n')


def test_default_metadata_is_inferred_for_generated_data(extension_client):
    def generate(_request):
        return ca.DataResponse(pd.DataFrame({
            "count": pd.Series([2, None], dtype="Int64"),
            "price": pd.Series([3.5, None], dtype="Float64"),
            "label": pd.Series(["example", None], dtype="string"),
            "timestamp": pd.to_datetime(["2026-01-15T09:30:00Z", None]),
        }), [])

    response = extension_client(generate, tables=[], extension_type=ca.ExtensionType.DATA).invoke()

    assert response.status_code == 200
    assert response.container["columns"] == [
        column("count", "int64", attributeGroupName="data"),
        column("price", "float64", attributeGroupName="data"),
        column("label", "string", attributeGroupName="data"),
        column("timestamp", "zonedDateTime", attributeGroupName="data"),
    ]
    assert response.rows == [
        ["count", "price", "label", "timestamp"], ["2", "3.5", "example", "2026-01-15T09:30:00Z"],
        ["", "NaN", "", ""],
    ]


def test_remove_strategy_only_returns_columns_with_metadata_without_changing_callers_data(extension_client):
    data = pd.DataFrame({"published": [1], "temporary": [2]})
    metadata = [ca.ColumnMetadata(name="published", print_name="Published", data_type=ca.DataType.INT64)]

    def generate(_request):
        return ca.DataResponse(data, metadata, missing_metadata_strategy=ca.MissingMetadataStrategy.REMOVE_DATA_COLUMNS)

    response = extension_client(generate, tables=[], extension_type=ca.ExtensionType.DATA).invoke()

    assert response.status_code == 200
    assert response.rows == [["published"], ["1"]]
    assert [item["name"] for item in response.container["columns"]] == ["published"]
    assert list(data.columns) == ["published", "temporary"]
    assert len(metadata) == 1


def test_strict_strategy_rejects_an_undocumented_response_column(extension_client):
    def generate(_request):
        return ca.DataResponse(pd.DataFrame({"undocumented": [1]}), [],
                               missing_metadata_strategy=ca.MissingMetadataStrategy.RAISE_EXCEPTION)

    with pytest.raises(ValueError):
        extension_client(generate, tables=[], extension_type=ca.ExtensionType.DATA).invoke()


@pytest.mark.parametrize("problem", ["duplicate-metadata", "metadata-without-data", "no-columns"])
def test_invalid_response_data_is_rejected(extension_client, problem):
    def generate(_request):
        item = ca.ColumnMetadata(name="value", print_name="Value", data_type=ca.DataType.INT64)
        if problem == "duplicate-metadata":
            return ca.DataResponse(pd.DataFrame({"value": [1]}), [item, item])
        if problem == "metadata-without-data":
            return ca.DataResponse(pd.DataFrame({"other": [1]}), [item])
        return ca.DataResponse(pd.DataFrame(), [])

    with pytest.raises(ValueError):
        extension_client(generate, tables=[], extension_type=ca.ExtensionType.DATA).invoke()


def test_author_can_explicitly_allow_a_response_without_columns(extension_client):
    def generate(_request):
        response = ca.DataResponse(pd.DataFrame(), [])
        response.runtime_validation_disabled = True
        return response

    response = extension_client(generate, tables=[], extension_type=ca.ExtensionType.DATA).invoke()

    assert response.status_code == 200
    assert response.text == ""
    assert response.container["columns"] == []


def test_geometry_output_accepts_shapely_values_and_missing_locations(extension_client):
    def generate(_request):
        return ca.DataResponse(pd.DataFrame({"location": [Point(8.4, 49), None]}), [
            ca.ColumnMetadata(name="location", print_name="Location", data_type=ca.DataType.GEOMETRY,
                              geometry_type=ca.GeometryType.POINT, srs="EPSG:4326"),
        ])

    response = extension_client(generate, tables=[], extension_type=ca.ExtensionType.DATA).invoke()

    assert response.status_code == 200
    assert response.text == '"location"\r\n"POINT (8.4 49)"\r\n\r\n'
    assert response.container["columns"] == [
        column("location", "geometry", printName="Location", attributeGroupName="data",
               geometryType="point", srs="EPSG:4326"),
    ]


def test_geometry_output_rejects_raw_wkt_strings(extension_client):
    def generate(_request):
        return ca.DataResponse(pd.DataFrame({"location": ["POINT (8.4 49)"]}), [
            ca.ColumnMetadata(name="location", print_name="Location", data_type=ca.DataType.GEOMETRY,
                              geometry_type=ca.GeometryType.POINT, srs="EPSG:4326"),
        ])

    with pytest.raises(TypeError):
        extension_client(generate, tables=[], extension_type=ca.ExtensionType.DATA).invoke()


@pytest.mark.parametrize("response_class,content,content_type", [
    (ca.TextResponse, "Grüße 世界\nSecond line", "text/plain;charset=utf-8"),
    (ca.UrlResponse, "https://example.org/report?city=M%C3%BCnchen", "text/uri-list"),
    (ca.ImageResponse, b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+a9X8AAAAASUVORK5CYII="
    ), "image/png"),
], ids=["text", "url", "png-image"])
def test_visual_response_preserves_content_and_declares_its_media_type(extension_client, response_class, content,
                                                                    content_type):
    def visualise(_request):
        return response_class(content)

    response = extension_client(visualise, tables=[], extension_type=ca.ExtensionType.VISUAL).invoke()

    assert response.status_code == 200
    assert response.content == (content.encode("utf-8") if isinstance(content, str) else content)
    assert response.container == {"name": "response-data", "type": content_type}


@pytest.mark.parametrize("status", [400, 422])
def test_business_error_reaches_the_client_as_json_with_the_requested_status(extension_client, status):
    def analyse(_request):
        return ca.ErrorResponse("Keine gültigen Daten — please choose another column", status=status)

    response = extension_client(analyse, tables=[]).invoke()

    assert response.status_code == status
    assert response.content_type == "application/json"
    assert response.json == {"message": "Keine gültigen Daten — please choose another column"}
    assert response.parts == {}


def test_requests_to_the_same_extension_do_not_share_parameter_values(extension_client):
    def analyse(request):
        return ca.TextResponse(str(request.parameters.get("input", "absent")))

    client = extension_client(analyse, tables=[])

    assert client.invoke(parameters=[parameter("input", "int64", 1)]).text == "1"
    assert client.invoke(parameters=[parameter("input", "int64", 2)]).text == "2"
    assert client.invoke().text == "absent"
