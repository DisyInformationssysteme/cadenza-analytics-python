"""Example module for running a disy Cadenza analytics extension that
 will execute a basic enrichment."""
import pandas as pd

import cadenzaanalytics as ca


def enrichment_basic_analytics_function(metadata: ca.RequestMetadata, data: pd.DataFrame):
    id_column_metadata = metadata.get_id_column()

    df_data = pd.DataFrame()
    df_data[id_column_metadata.name] = data[id_column_metadata.name]
    df_data["new_value"] = "value"

    result_metadata = [
        id_column_metadata,
        ca.ColumnMetadata(
            name="new_value",
            print_name="New value",
            data_type= ca.DataType.STRING,
            role=ca.AttributeRole.DIMENSION
        )
    ]

    return ca.EnrichmentResponse(df_data, result_metadata)


any_attribute_group = ca.AttributeGroup(
    name="any_data",
    print_name="Any attribute",
    # any except geometry, these cannot be mixed to make it clear when a geometry or a related
    # non-geometry attribute is wanted from the user
    data_types=[ca.DataType.STRING, ca.DataType.INT64, ca.DataType.FLOAT64, ca.DataType.ZONEDDATETIME],
    min_attributes=1
)

enrichment_echo_extension = ca.CadenzaAnalyticsExtension(
    relative_path="basic-extension",
    analytics_function=enrichment_basic_analytics_function,
    print_name="Example Basic Enrichment Extension",
    extension_type=ca.ExtensionType.ENRICHMENT,
    attribute_groups=[any_attribute_group]
)

analytics_service = ca.CadenzaAnalyticsExtensionService()
analytics_service.add_analytics_extension(enrichment_echo_extension)

if __name__ == '__main__':
    analytics_service.run_development_server(5005)
