"""Example module for running a disy Cadenza analytics extension that
 will execute a basic enrichment."""
import pandas as pd

import cadenzaanalytics as ca


def enrichment_basic_analytics_function(request: ca.AnalyticsRequest):
    table = request["table"]

    df_data = pd.DataFrame()
    df_data[table.metadata.id_names] = table.data[table.metadata.id_names]
    df_data["new_value"] = "value"

    result_metadata = [
        table.metadata.id_columns,
        ca.ColumnMetadata(
            name="new_value",
            print_name="New value",
            data_type= ca.DataType.STRING,
            role=ca.AttributeRole.DIMENSION
        )
    ]

    return ca.EnrichmentResponse(df_data, result_metadata)


def enrichment_signum_analytics_function(request: ca.AnalyticsRequest):
    signum_column = ca.ColumnMetadata(name="signum", print_name="Signum",
                                      data_type=ca.DataType.INT64,
                                      role=ca.AttributeRole.DIMENSION)
    def get_signum(row):
        return pd.Series(
            {signum_column.name: sign(row["number"])}, index=[signum_column.name]
        )

    def sign(value) -> int:
        if value > 0:
            return 1
        if value < 0:
            return -1
        return 0

    return request['table'].to_enrichment(new_columns=[signum_column], row_mapper=get_signum)

any_attribute_group = ca.AttributeGroup(
    name="any_data",
    print_name="Any attribute",
    # any except geometry, these cannot be mixed to make it clear when a geometry or a related
    # non-geometry attribute is wanted from the user
    data_types=[ca.DataType.STRING, ca.DataType.INT64, ca.DataType.FLOAT64, ca.DataType.ZONEDDATETIME],
    min_attributes=1
)

any_number_group = ca.AttributeGroup(
    name="number",
    print_name="Any number",
    data_types=[ca.DataType.INT64, ca.DataType.FLOAT64],
    min_attributes=1,
    max_attributes=1
)

enrichment_echo_extension = ca.CadenzaAnalyticsExtension(
    relative_path="basic-extension",
    analytics_function=enrichment_basic_analytics_function,
    print_name="Example Basic Enrichment Extension",
    extension_type=ca.ExtensionType.ENRICHMENT,
    tables=[ca.Table(name="table", attribute_groups=[any_attribute_group])]
)

enrichment_signum_extension = ca.CadenzaAnalyticsExtension(
    relative_path="signum-extension",
    analytics_function=enrichment_signum_analytics_function,
    print_name="Example Signum Enrichment Extension",
    extension_type=ca.ExtensionType.ENRICHMENT,
    tables=[ca.Table(name="table", attribute_groups=[any_number_group])]
)

analytics_service = ca.CadenzaAnalyticsExtensionService()
analytics_service.add_analytics_extension(enrichment_echo_extension)
analytics_service.add_analytics_extension(enrichment_signum_extension)

if __name__ == '__main__':
    analytics_service.run_development_server(5005)
