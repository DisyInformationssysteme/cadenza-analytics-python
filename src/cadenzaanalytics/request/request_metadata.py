from typing import List, Dict, Optional

from cadenzaanalytics.data.column_metadata import ColumnMetadata


# pylint: disable=protected-access
class RequestMetadata:
    """A class representing metadata for a request.
    """
    def __init__(self, request_metadata: dict):
        self._request_metadata = request_metadata

    def get_column(self, name: str) -> Optional[ColumnMetadata]:
        """Get metadata for a specific column by name.

        Parameters
        ----------
        name : str
            The name of the column.

        Returns
        -------
        ColumnMetadata | None
            Metadata for the column if found, else None.
        """
        if self.has_columns():
            for column in self._get_columns():
                if column["name"] == name:
                    return ColumnMetadata._from_dict(column)

        return None

    def get_column_by_attribute_group(self, attribute_group) -> Optional[ColumnMetadata]:
        """Get a column by its attribute group.

        Returns
        -------
        Optional[ColumnMetadata]
            The column metadata corresponding to the given attribute group, if found; otherwise, None.
        """        
        if self.has_columns():
            for column in self._get_columns():
                if column['attributeGroupName'] == attribute_group:
                    return ColumnMetadata._from_dict(column)
        return None

    def get_all_columns_by_attribute_groups(self) -> Dict[str, List[ColumnMetadata]]:
        """Get all columns grouped by attribute groups.

        Returns
        -------
        Dict[str, List[ColumnMetadata]]
            A dictionary where keys are attribute group names and values are lists of corresponding column metadata.
        """        
        grouped_columns = {}
        columns = self._get_columns() if self.has_columns() else []
        for column in columns:
            if column['attributeGroupName'] not in grouped_columns:
                grouped_columns[column['attributeGroupName']] = []

            grouped_columns[column['attributeGroupName']].append(ColumnMetadata._from_dict(column))

        return grouped_columns

    def get_all_columns(self) -> List[ColumnMetadata]:
        """Get all columns.

        Returns
        -------
        List[ColumnMetadata]
            A list of all column metadata.
        """     
        columns = self._get_columns() if self.has_columns() else []
        return [ColumnMetadata._from_dict(column) for column in columns]

    def get_parameters(self) -> Dict[str, str]:
        """Get parameters of the request.

        Returns
        -------
        dict[str, str]
            Parameters of the request.
        """  
        return self._request_metadata['parameters']

    def get_parameter(self, name: str) -> Optional[str]:
        """Get a specific parameter value by name.

        Parameters
        ----------
        name : str
            The name of the parameter.

        Returns
        -------
        str
            The value of the parameter if found, else an empty string.
        """
        if name in self._request_metadata['parameters']:
            return self._request_metadata['parameters'][name]
        return None

    def has_columns(self) -> bool:
        """Check if the request has columns metadata.

        Returns
        -------
        bool
            True if the request has columns metadata, False otherwise.
        """ 
        return (len(self._request_metadata['dataContainers']) > 0
                and "columns" in self._request_metadata['dataContainers'][0])

    def _get_columns(self):
        return self._request_metadata['dataContainers'][0]['columns']
