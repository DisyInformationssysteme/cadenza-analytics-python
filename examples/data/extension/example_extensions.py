"""Example module for running a disy Cadenza analytics extension that
 will show a (static) image in disy Cadenza"""
import pandas as pd

import cadenzaanalytics as ca


def minimal_data_analytics_function(request: ca.AnalyticsRequest):
    # pylint: disable=unused-argument
    return ca.DataResponse(pd.DataFrame(), [])


def minimal_data_echo_analytics_function(request: ca.AnalyticsRequest):
    data = request["table"].data
    metadata = request["table"].metadata
    return ca.DataResponse(data, metadata.get_columns())

def data_echo_analytics_function(request: ca.AnalyticsRequest):
    # pylint: disable=unused-variable
    data = request["table"].data
    metadata = request["table"].metadata
    add_nulls = request.parameters["append_nulls"].value
    append_rows_count = max(request.parameters["append_rows_count"].value, 1)
    user_chosen_attributes = metadata.groups["any_data"]
    some_attribute = metadata.columns["any_data_1"]
    if add_nulls:
        # add a row with only None values if user requested it, add as many (min 1) as requested
        added = pd.DataFrame([[None] * len(data.columns)] * append_rows_count, columns=data.columns)
        data = pd.concat([data, added])
    return ca.DataResponse(data, metadata.get_columns())


any_attribute_group = ca.AttributeGroup(
    name="any_data",
    print_name="Any attribute",
    # any except geometry, these cannot be mixed to make it clear when a geometry or a related
    # non-geometry attribute is wanted from the user
    data_types=[ca.DataType.STRING, ca.DataType.INT64, ca.DataType.FLOAT64, ca.DataType.ZONEDDATETIME],
    min_attributes=1
)
any_geometry_group = ca.AttributeGroup(
    name="any_geometry",
    print_name="Any geometry",
    data_types=[ca.DataType.GEOMETRY],
    geometry_types=[ca.GeometryType.POINT, ca.GeometryType.MULTIPOINT,
                    ca.GeometryType.LINESTRING, ca.GeometryType.MULTILINESTRING,
                    ca.GeometryType.POLYGON, ca.GeometryType.MULTIPOLYGON],
    requested_srs="EPSG:3857",
    max_attributes=1
)

minimal_data_extension = ca.CadenzaAnalyticsExtension(
    relative_path="minimal-data-extension",
    analytics_function=minimal_data_analytics_function,
    print_name="Example Minimal Data Extension",
    extension_type=ca.ExtensionType.DATA,
    tables=[],
    parameters=[]
)
minimal_data_echo_extension = ca.CadenzaAnalyticsExtension(
    relative_path="minimal-data-echo-extension",
    analytics_function=minimal_data_echo_analytics_function,
    print_name="Example Minimal Echo Data Extension",
    extension_type=ca.ExtensionType.DATA,
    tables=[ca.Table(name="table", attribute_groups=[any_attribute_group])],
    parameters=[]
)
data_echo_extension = ca.CadenzaAnalyticsExtension(
    relative_path="data-echo-extension",
    analytics_function=data_echo_analytics_function,
    print_name="Example Echo Data Extension",
    extension_type=ca.ExtensionType.DATA,
    tables=[ca.Table(name="table", attribute_groups=[any_attribute_group, any_geometry_group])],
    parameters=[ca.Parameter(name="append_nulls", print_name="Append row with null values",
                             parameter_type=ca.ParameterType.BOOLEAN, default_value=False, required=False),
                ca.Parameter(name="append_rows_count", print_name="How many rows with null values should be appended?",
                             parameter_type=ca.ParameterType.INT64, default_value=1, required=True),
                ca.Parameter(name="float_param", print_name="Not used float",
                             parameter_type=ca.ParameterType.FLOAT64, required=False),
                ca.Parameter(name="geom_param", print_name="Not used geometry",
                             parameter_type=ca.ParameterType.GEOMETRY,
                             geometry_types=[ca.GeometryType.MULTIPOLYGON], requested_srs="EPSG:3857", required=False),
                ca.Parameter(name="datetime_param", print_name="Not used datetime",
                             parameter_type=ca.ParameterType.ZONEDDATETIME, required=False),
                ca.Parameter(name="string_param", print_name="Not used string",
                             parameter_type=ca.ParameterType.STRING, required=False)]
)

analytics_service = ca.CadenzaAnalyticsExtensionService()
analytics_service.add_analytics_extension(minimal_data_extension)
analytics_service.add_analytics_extension(minimal_data_echo_extension)
analytics_service.add_analytics_extension(data_echo_extension)

if __name__ == '__main__':
    analytics_service.run_development_server(5005)
