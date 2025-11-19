from typing import List, Dict, Optional

from cadenzaanalytics.data.column_metadata import ColumnMetadata
from cadenzaanalytics.data.attribute_group import AttributeGroup


# pylint: disable=protected-access
class RequestMetadata:
    """A class representing the metadata for an analytics request.
    """
    def __init__(self, request_metadata: dict):
        self._request_metadata = request_metadata

    def __getitem__(self, key) -> ColumnMetadata:
        """Returns the column metadata object for a specific column accessed by its name.

        Parameters
        ----------
        key : str
            The name of the column.

        Returns
        -------
        ColumnMetadata
            Metadata for the column
        """

        if self.has_columns():
            for column in self._get_columns():
                if column["name"] == key:
                    return ColumnMetadata._from_dict(column)

        raise KeyError(f"Key '{key}' not found.")

    @property
    def id(self) -> Optional[ColumnMetadata]:
        """Returns the id column metadata object.

        Returns
        -------
        ColumnMetadata | None
            Metadata for the column if found, else None.
        """
        if len(self.groups[AttributeGroup.ID_ATTRIBUTE_GROUP_NAME]) > 0:
            return self.groups[AttributeGroup.ID_ATTRIBUTE_GROUP_NAME][0]

        return None

    @property
    def groups(self) -> Dict[str, List[ColumnMetadata]]:
        """Returns all column metadata objects grouped by its attribute groups.

        Returns
        -------
        Dict[str, List[ColumnMetadata]]
            A dictionary where the keys are the attribute group names and values are lists of corresponding
             column metadata objects.
        """
        grouped_columns = {}
        columns = self._get_columns() if self.has_columns() else []
        for column in columns:
            if column['attributeGroupName'] not in grouped_columns:
                grouped_columns[column['attributeGroupName']] = []

            grouped_columns[column['attributeGroupName']].append(ColumnMetadata._from_dict(column))

        return grouped_columns

    @property
    def columns(self) -> Dict[str, ColumnMetadata]:
        """Returns a column metadata object for by its column name."""
        columns = self._get_columns() if self.has_columns() else []
        return {c["name"]: ColumnMetadata._from_dict(c) for c in columns}


    def get_first_column_of_attribute_group(self, attribute_group) -> Optional[ColumnMetadata]:
        """Returns the first column metadata object of the given attribute group.

        Returns
        -------
        Optional[ColumnMetadata]
            The column metadata of the first column in the given attribute group. If no column metadata for the
            attribute group was send None is returned.
        """
        if self.has_columns():
            for column in self._get_columns():
                if column['attributeGroupName'] == attribute_group:
                    return ColumnMetadata._from_dict(column)
        return None



    def get_columns(self) -> List[ColumnMetadata]:
        """Returns a list of all column metadata objects.

        Returns
        -------
        List[ColumnMetadata]
            A list of all column metadata objects.
        """
        columns = self._get_columns() if self.has_columns() else []
        return [ColumnMetadata._from_dict(column) for column in columns]

    def has_columns(self) -> bool:
        """Check if the analytics request has columns with corresponding metadata.

        Returns
        -------
        bool
            True if the request has columns with corresponding metadata, False otherwise.
        """
        return (self._request_metadata['dataContainers'] != []
                and len(self._request_metadata['dataContainers'][0]['columns']) > 0)

    def _get_columns(self):
        return self._request_metadata['dataContainers'][0]['columns']
