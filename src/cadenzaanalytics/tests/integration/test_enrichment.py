"""Enrichment results retain the identifiers Cadenza needs to match input rows."""

import pandas as pd
import pytest

import cadenzaanalytics as ca

from .client import column


def test_enrichment_automatically_carries_input_ids_into_the_result(extension_client, orders_payload):
    def enrich(request):
        orders = request["orders"].data
        result = pd.DataFrame({"double_quantity": orders["quantity"] * 2})
        return ca.EnrichmentResponse(result, [
            ca.ColumnMetadata(name="double_quantity", print_name="Double quantity", data_type=ca.DataType.INT64),
        ])

    response = extension_client(enrich, extension_type=ca.ExtensionType.ENRICHMENT).invoke(**orders_payload)

    assert response.status_code == 200
    assert response.rows == [["double_quantity", "order_id"], ["4", "101"], ["2", "102"], ["", "103"]]
    assert response.container["columns"] == [
        column("double_quantity", "int64", printName="Double quantity", attributeGroupName="data"),
        orders_payload["metadata"]["dataContainers"][0]["columns"][0],
    ]


def test_remove_strategy_keeps_automatic_ids_and_removes_unpublished_columns(extension_client, orders_payload):
    def enrich(request):
        result = request["orders"].data.copy()
        result["double_quantity"] = result["quantity"] * 2
        return ca.EnrichmentResponse(result, [
            ca.ColumnMetadata(name="double_quantity", print_name="Double quantity", data_type=ca.DataType.INT64),
        ], missing_metadata_strategy=ca.MissingMetadataStrategy.REMOVE_DATA_COLUMNS)

    response = extension_client(enrich, extension_type=ca.ExtensionType.ENRICHMENT).invoke(**orders_payload)

    assert response.status_code == 200
    assert response.rows == [["order_id", "double_quantity"], ["101", "4"], ["102", "2"], ["103", ""]]
    assert {item["name"] for item in response.container["columns"]} == {"order_id", "double_quantity"}


def test_multiple_id_columns_are_retained_together(extension_client):
    def enrich(request):
        result = pd.DataFrame({"double_amount": request["orders"].data["amount"] * 2})
        return ca.EnrichmentResponse(result, [])

    response = extension_client(enrich, extension_type=ca.ExtensionType.ENRICHMENT).invoke(columns=[
        column("order_id", "int64", attributeGroupName="net.disy.cadenza.keyAttributeGroup"),
        column("region", attributeGroupName="net.disy.cadenza.keyAttributeGroup"),
        column("amount", "int64"),
    ], csv_data='"order_id";"region";"amount"\r\n"1";"north";"10"\r\n"1";"south";"20"\r\n')

    assert response.status_code == 200
    assert response.rows == [["double_amount", "order_id", "region"], ["20", "1", "north"], ["40", "1", "south"]]
    id_columns = [item["name"] for item in response.container["columns"]
                  if item["attributeGroupName"] == "net.disy.cadenza.keyAttributeGroup"]
    assert id_columns == ["order_id", "region"]


def test_explicit_ids_allow_an_extension_to_reorder_results(extension_client, orders_payload):
    def enrich(request):
        table = request["orders"]
        result = table.data[["order_id"]].iloc[::-1].copy()
        result["label"] = ["third", "second", "first"]
        return ca.EnrichmentResponse(result, [
            *table.metadata.ids,
            ca.ColumnMetadata(name="label", print_name="Label", data_type=ca.DataType.STRING),
        ])

    response = extension_client(enrich, extension_type=ca.ExtensionType.ENRICHMENT).invoke(**orders_payload)

    assert response.status_code == 200
    assert response.rows == [["order_id", "label"], ["103", "third"], ["102", "second"], ["101", "first"]]


@pytest.mark.parametrize("problem", ["wrong-id-name", "declared-id-missing-from-data"])
def test_inconsistent_enrichment_ids_are_rejected(extension_client, orders_payload, problem):
    def enrich(request):
        if problem == "wrong-id-name":
            return ca.EnrichmentResponse(pd.DataFrame({"wrong_id": [1, 2, 3]}), [
                ca.ColumnMetadata(name="wrong_id", print_name="Wrong ID", data_type=ca.DataType.INT64,
                                  attribute_group_name=ca.AttributeGroup.ID_ATTRIBUTE_GROUP_NAME),
            ])
        return ca.EnrichmentResponse(pd.DataFrame({"value": [1, 2, 3]}), request["orders"].metadata.ids)

    with pytest.raises(ValueError):
        extension_client(enrich, extension_type=ca.ExtensionType.ENRICHMENT).invoke(**orders_payload)


def test_enrichment_requires_an_input_table(extension_client):
    def enrich(_request):
        return ca.EnrichmentResponse(pd.DataFrame({"value": [1]}), [])

    with pytest.raises(ValueError):
        extension_client(enrich, tables=[], extension_type=ca.ExtensionType.ENRICHMENT).invoke()
