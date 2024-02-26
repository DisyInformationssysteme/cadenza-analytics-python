from cadenzaanalytics.data.column_metadata import ColumnMetadata


# pylint: disable=protected-access
class RequestMetadata:
    def __init__(self, request_metadata: dict):
        self._request_metadata = request_metadata

    def get_column_metadata(self, name: str) -> ColumnMetadata | None:
        if self.has_columns():
            for column in self._request_metadata['dataContainers'][0]['columns']:
                if column["name"] == name:
                    return ColumnMetadata._from_dict(column)

        return None

    def get_columns_by_attribute_group(self) -> dict[str, list[ColumnMetadata]] | None:
        if self.has_columns():
            grouped_columns = {}

            for column in self._request_metadata['dataContainers'][0]['columns']:
                if column['attributeGroupName'] not in grouped_columns:
                    grouped_columns[column['attributeGroupName']] = []

                grouped_columns[column['attributeGroupName']].append(ColumnMetadata._from_dict(column))

            return grouped_columns

        return None

    def get_parameters(self) -> dict[str, str]:
        return self._request_metadata['parameters']

    def get_parameter(self, name: str) -> str:
        if name in self._request_metadata['parameters']:
            return self._request_metadata['parameters'][name]
        return ""

    def has_columns(self) -> bool:
        return (len(self._request_metadata['dataContainers']) > 0
                and "columns" in self._request_metadata['dataContainers'][0])
