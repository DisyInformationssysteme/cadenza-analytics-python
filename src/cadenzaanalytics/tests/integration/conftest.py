"""Fresh extensions and readable, client-authored input for each scenario."""

from pathlib import Path
import json

import pytest

import cadenzaanalytics as ca

from .client import ExtensionClient


@pytest.fixture
def extension_client():
    def create(analytics_function, *, extension_type=ca.ExtensionType.VISUAL, tables=None, parameters=None):
        if tables is None:
            tables = [ca.Table(name="orders", attribute_groups=[
                ca.AttributeGroup(
                    name="values", print_name="Values",
                    data_types=[ca.DataType.STRING, ca.DataType.INT64, ca.DataType.FLOAT64, ca.DataType.ZONEDDATETIME],
                ),
                ca.AttributeGroup(
                    name="location", print_name="Location", data_types=[ca.DataType.GEOMETRY],
                    geometry_types=[ca.GeometryType.POINT], requested_srs="EPSG:4326",
                ),
            ])]
        return ExtensionClient(ca.CadenzaAnalyticsExtension(
            relative_path="orders", print_name="Order analysis", analytics_function=analytics_function,
            extension_type=extension_type, tables=tables, parameters=parameters,
        ))
    return create


@pytest.fixture
def orders_payload():
    fixtures = Path(__file__).parent / "fixtures"
    metadata = json.loads((fixtures / "orders.json").read_text(encoding="utf-8"))
    # Keep fixtures easy to edit; the wire protocol uses CRLF line endings.
    csv_data = (fixtures / "orders.csv").read_text(encoding="utf-8").replace("\n", "\r\n")
    return {"metadata": metadata, "csv_data": csv_data}
