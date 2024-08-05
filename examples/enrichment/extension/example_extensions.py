"""Example module for running a disy Cadenza analytics extension that
 will show a (static) image in disy Cadenza"""
import pandas as pd

import cadenzaanalytics as ca


def enrichment_echo_analytics_function(metadata: ca.RequestMetadata, data: pd.DataFrame):
    # pylint: disable=unused-argument
    response_columns = metadata.get_columns_by_attribute_group()['any_data']
    response_column_names = [c.name for c in response_columns]
    return ca.RowWiseMappingCsvResponse(
        response_columns,
        lambda row: row[response_column_names])


any_attribute_group = ca.AttributeGroup(
    name="any_data",
    print_name="Any attribute",
    # any except geometry, these cannot be mixed to make it clear when a geometry or a related
    # non-geometry attribute is wanted from the user
    data_types=[ca.DataType.STRING, ca.DataType.INT64, ca.DataType.FLOAT64, ca.DataType.ZONEDDATETIME],
    min_attributes=1
)

enrichment_echo_extension = ca.CadenzaAnalyticsExtension(
    relative_path="echo-extension",
    analytics_function=enrichment_echo_analytics_function,
    print_name="Example Echo Enrichment Extension",
    extension_type=ca.ExtensionType.ENRICHMENT,
    attribute_groups=[any_attribute_group]
)

analytics_service = ca.CadenzaAnalyticsExtensionService()
analytics_service.add_analytics_extension(enrichment_echo_extension)

if __name__ == '__main__':
    analytics_service.run_development_server(5005)
