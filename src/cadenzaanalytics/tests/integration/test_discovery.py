"""Discover and configure extensions as a client or extension author."""

import pytest

import cadenzaanalytics as ca


def unused_callback(_request):
    pytest.fail("Discovery and capability requests must not execute analytics")


def test_new_service_has_no_extensions():
    service = ca.CadenzaAnalyticsExtensionService()

    response = service.app.test_client().get("/")

    assert response.status_code == 200
    assert response.json == {"extensions": [], "cadenzaAnalyticsVersion": ca.__version__}


def test_client_can_discover_each_extension_and_fetch_its_capabilities():
    service = ca.CadenzaAnalyticsExtensionService()
    for kind in (ca.ExtensionType.DATA, ca.ExtensionType.ENRICHMENT, ca.ExtensionType.VISUAL):
        service.add_analytics_extension(ca.CadenzaAnalyticsExtension(
            relative_path=str(kind), print_name=f"Example {kind}",
            analytics_function=unused_callback, extension_type=kind,
        ))
    client = service.app.test_client()

    discovery = client.get("/")

    assert discovery.json == {
        "extensions": [
            {"relativePath": kind, "extensionPrintName": f"Example {kind}", "extensionType": kind}
            for kind in ("data", "enrichment", "visual")
        ],
        "cadenzaAnalyticsVersion": ca.__version__,
    }
    for entry in discovery.json["extensions"]:
        capabilities = client.get("/" + entry["relativePath"])
        assert capabilities.status_code == 200
        assert capabilities.json == {
            "printName": entry["extensionPrintName"], "extensionType": entry["extensionType"],
            "attributeGroups": [], "cadenzaAnalyticsVersion": ca.__version__,
        }


def test_capabilities_describe_attribute_constraints_and_parameter_choices(extension_client):
    client = extension_client(unused_callback, tables=[ca.Table(name="orders", attribute_groups=[
        ca.AttributeGroup(
            name="location", print_name="Delivery location", data_types=[ca.DataType.GEOMETRY],
            geometry_types=[ca.GeometryType.POINT, ca.GeometryType.MULTIPOINT], requested_srs="EPSG:4326",
            min_attributes=1, max_attributes=2,
        ),
    ])], parameters=[
        ca.Parameter(name="mode", print_name="Mode", parameter_type=ca.ParameterType.SELECT,
                     options=["fast", "accurate"], default_value="fast", required=True),
        ca.Parameter(name="enabled", print_name="Enabled", parameter_type=ca.ParameterType.BOOLEAN,
                     default_value=False),
        ca.Parameter(name="area", print_name="Area", parameter_type=ca.ParameterType.GEOMETRY,
                     geometry_types=[ca.GeometryType.POLYGON], requested_srs="EPSG:4326"),
    ])

    response = client.http.get(client.path)

    assert response.status_code == 200
    assert response.json["attributeGroups"] == [{
        "name": "location", "printName": "Delivery location", "dataTypes": ["geometry"],
        "geometryTypes": ["point", "multipoint"], "requestedSrs": "EPSG:4326",
        "minAttributes": 1, "maxAttributes": 2,
    }]
    assert response.json["parameters"] == [
        {"name": "mode", "printName": "Mode", "parameterType": "select", "options": ["fast", "accurate"],
         "defaultValue": "fast", "required": True},
        {"name": "enabled", "printName": "Enabled", "parameterType": "boolean",
         "defaultValue": False, "required": False},
        {"name": "area", "printName": "Area", "parameterType": "geometry",
         "geometryTypes": ["polygon"], "requestedSrs": "EPSG:4326", "required": False},
    ]


def test_registering_an_existing_path_is_rejected():
    service = ca.CadenzaAnalyticsExtensionService()
    extension = ca.CadenzaAnalyticsExtension(
        relative_path="orders", print_name="Orders", analytics_function=unused_callback,
        extension_type=ca.ExtensionType.DATA,
    )
    service.add_analytics_extension(extension)

    with pytest.raises(ValueError, match="already in use"):
        service.add_analytics_extension(extension)


@pytest.mark.parametrize("callback", [lambda: None, lambda first, second: None], ids=["no-request", "two-arguments"])
def test_registering_a_callback_without_one_request_argument_is_rejected(callback):
    service = ca.CadenzaAnalyticsExtensionService()

    with pytest.raises(ValueError, match="exactly 1"):
        service.add_analytics_extension(ca.CadenzaAnalyticsExtension(
            relative_path="orders", print_name="Orders", analytics_function=callback,
            extension_type=ca.ExtensionType.DATA,
        ))


def test_extension_configuration_rejects_multiple_tables():
    with pytest.raises(ValueError, match="At most one table"):
        ca.CadenzaAnalyticsExtension(
            relative_path="orders", print_name="Orders", analytics_function=unused_callback,
            extension_type=ca.ExtensionType.DATA,
            tables=[ca.Table(name="first", attribute_groups=[]), ca.Table(name="second", attribute_groups=[])],
        )
