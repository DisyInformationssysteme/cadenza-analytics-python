"""Example module for running a disy Cadenza analytics extension that
 will show a (static) image in disy Cadenza"""
import pandas as pd

import cadenzaanalytics as ca


def image_analytics_function(metadata: ca.RequestMetadata, data: pd.DataFrame):
    # pylint: disable=unused-argument
    with open("example_image.png", "rb") as image_file:
        image = image_file.read()

    return ca.ImageResponse(image)


def echo_analytics_function(metadata: ca.RequestMetadata, data: pd.DataFrame):
    return ca.CsvResponse(data, metadata.get_columns_by_attribute_group()['any_data'])


image_attribute_group = ca.AttributeGroup(
    name="data",
    print_name="Data",
    data_types=[ca.DataType.STRING]
)

any_attribute_group = ca.AttributeGroup(
    name="any_data",
    print_name="Any attribute",
    # any except geometry, these cannot be mixed to make it clear when a geometry or a related
    # non-geometry attribute is wanted from the user
    data_types=[ca.DataType.STRING, ca.DataType.INT64, ca.DataType.FLOAT64, ca.DataType.ZONEDDATETIME],
    min_attributes=1
)

image_extension = ca.CadenzaAnalyticsExtension(
    relative_path="image-extension",
    analytics_function=image_analytics_function,
    print_name="Example Image Extension",
    extension_type=ca.ExtensionType.VISUALIZATION,
    attribute_groups=[image_attribute_group]
)

echo_extension = ca.CadenzaAnalyticsExtension(
    relative_path="echo-extension",
    analytics_function=echo_analytics_function,
    print_name="Example Echo Calculation Extension",
    extension_type=ca.ExtensionType.CALCULATION,
    attribute_groups=[any_attribute_group]
)

analytics_service = ca.CadenzaAnalyticsExtensionService()
analytics_service.add_analytics_extension(image_extension)
analytics_service.add_analytics_extension(echo_extension)

# run development server, remove in production environment
analytics_service.run(5005)
