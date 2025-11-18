"""Example module for running a disy Cadenza analytics extension that
 will show a (static) image in disy Cadenza"""
import pandas as pd

import cadenzaanalytics as ca


def image_analytics_function(metadata: ca.RequestMetadata, data: pd.DataFrame):
    # pylint: disable=unused-argument
    with open("resources/example_image.png", "rb") as image_file:
        image = image_file.read()

    return ca.ImageResponse(image)


image_attribute_group = ca.AttributeGroup(
    name="data",
    print_name="Data",
    data_types=[ca.DataType.STRING]
)

image_extension = ca.CadenzaAnalyticsExtension(
    relative_path="image-extension",
    analytics_function=image_analytics_function,
    print_name="Example Image Extension",
    extension_type=ca.ExtensionType.VISUAL,
    attribute_groups=[image_attribute_group]
)

analytics_service = ca.CadenzaAnalyticsExtensionService()
analytics_service.add_analytics_extension(image_extension)

if __name__ == '__main__':
    analytics_service.run_development_server(5005)
