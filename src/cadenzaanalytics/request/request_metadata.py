from typing import List, Dict

from cadenzaanalytics.data.column_metadata import ColumnMetadata


# pylint: disable=protected-access
class RequestMetadata:
    def __init__(self, request_metadata: dict):
        self._request_metadata = request_metadata

    def get_column(self, name: str) -> ColumnMetadata | None:
        if self.has_columns():
            for column in self._get_columns():
                if column["name"] == name:
                    return ColumnMetadata._from_dict(column)

        return None

    def get_column_by_attribute_group(self, attribute_group) -> ColumnMetadata | None:
        if self.has_columns():
            for column in self._get_columns():
                if column['attributeGroupName'] == attribute_group:
                    return ColumnMetadata._from_dict(column)
        return None

    def get_all_columns_by_attribute_groups(self) -> Dict[str, List[ColumnMetadata]]:
        grouped_columns = {}
        columns = self._get_columns() if self.has_columns() else []
        for column in columns:
            if column['attributeGroupName'] not in grouped_columns:
                grouped_columns[column['attributeGroupName']] = []

            grouped_columns[column['attributeGroupName']].append(ColumnMetadata._from_dict(column))

        return grouped_columns

    def get_all_columns(self) -> List[ColumnMetadata]:
        columns = self._get_columns() if self.has_columns() else []
        return [ColumnMetadata._from_dict(column) for column in columns]

    def get_parameters(self) -> Dict[str, str]:
        return self._request_metadata['parameters']

    def get_parameter(self, name: str) -> str | None:
        if name in self._request_metadata['parameters']:
            return self._request_metadata['parameters'][name]
        return None

    def has_columns(self) -> bool:
        return (len(self._request_metadata['dataContainers']) > 0
                and "columns" in self._request_metadata['dataContainers'][0])

    def _get_columns(self):
        return self._request_metadata['dataContainers'][0]['columns']
