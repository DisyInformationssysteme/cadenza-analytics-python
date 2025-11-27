import collections
from typing import List, Dict, Optional

from cadenzaanalytics.data.column_metadata import ColumnMetadata
from cadenzaanalytics.data.attribute_group import AttributeGroup


# pylint: disable=protected-access
class RequestMetadata(collections.abc.Mapping):
    """A class representing the metadata for an analytics request.
    """
    def __init__(self, request_metadata: dict):
        self._columns = [ColumnMetadata._from_dict(column)
                         for column
                         in RequestMetadata._parse_columns(request_metadata)]

    @staticmethod
    def _parse_columns(request_metadata: dict):
        _containers = request_metadata['dataContainers']
        _has_columns = _containers is not None and len(_containers) > 0 and len(_containers[0]['columns']) > 0
        raw_columns = _containers[0]['columns'] if _has_columns else []
        return raw_columns

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

        for column in self._columns:
            if column.name == key:
                return column

        raise KeyError(f"Column '{key}' not found.")

    def __iter__(self):
        return iter(c.name for c in self._columns)

    def __len__(self):
        return len(self._columns)

    def __contains__(self, key):
        for column in self._columns:
            if column.name == key:
                return True
        return False

    @property
    def ids(self) -> List[ColumnMetadata]:
        """Returns all id column metadata objects. Relevant for extensions of type ENRICHMENT
        to connect request and response data.

        Returns
        -------
        List[ColumnMetadata] | None
            Metadata for the id columns if found, else None.
        """
        return self.groups.get(AttributeGroup.ID_ATTRIBUTE_GROUP_NAME)

    @property
    def id_names(self) -> List[str]:
        """Returns all id column names. Relevant for extensions of type ENRICHMENT
        to connect request and response data by copying relevant id columns from the input data frame.

        Returns
        -------
        List[str] | None
            Metadata for the id columns if found, else None.
        """
        id_columns = self.ids
        return [c.name for c in id_columns] if id_columns else None

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
        for column in self._columns:
            grouped_columns.setdefault(column.attribute_group_name, []).append(column)

        return grouped_columns

    @property
    def columns(self) -> List[ColumnMetadata]:
        """Returns a list of all column metadata objects.

        Returns
        -------
        List[ColumnMetadata]
            A list of all column metadata objects.
        """
        return self._columns
