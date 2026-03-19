import collections
from typing import Iterator, List, Dict, Optional

from cadenzaanalytics.data.column_metadata import ColumnMetadata
from cadenzaanalytics.data.attribute_group import AttributeGroup


# pylint: disable=protected-access
class RequestMetadata(collections.abc.Mapping[str, ColumnMetadata]):
    """Metadata describing the columns in a request table.

    Provides access to column metadata by name and groupings by attribute group.
    """

    def __init__(self, request_metadata: dict) -> None:
        """Initialize RequestMetadata from a metadata dictionary.

        Parameters
        ----------
        request_metadata : dict
            Metadata dictionary from Cadenza containing data container and column information.
        """
        self._columns = [ColumnMetadata._from_dict(column)
                         for column
                         in RequestMetadata._parse_columns(request_metadata)]
        # Build index for O(1) lookups by column name
        self._columns_by_name: Dict[str, ColumnMetadata] = {col.name: col for col in self._columns}
        # Build groups index once at initialization
        self._groups: Dict[str, List[ColumnMetadata]] = {}
        for column in self._columns:
            self._groups.setdefault(column.attribute_group_name, []).append(column)

    @staticmethod
    def _parse_columns(request_metadata: dict) -> List[dict]:
        _containers = request_metadata['dataContainers']
        _has_columns = _containers is not None and len(_containers) > 0 and len(_containers[0]['columns']) > 0
        raw_columns = _containers[0]['columns'] if _has_columns else []
        return raw_columns

    def __getitem__(self, key: str) -> ColumnMetadata:
        """Returns the column metadata object for a specific column accessed by its name.

        Parameters
        ----------
        key : str
            The name of the column.

        Returns
        -------
        ColumnMetadata
            Metadata for the column.

        Raises
        ------
        KeyError
            If no column with the given name exists.
        """
        try:
            return self._columns_by_name[key]
        except KeyError:
            raise KeyError(f"Column '{key}' not found.") from None

    def __iter__(self) -> Iterator[str]:
        return iter(c.name for c in self._columns)

    def __len__(self) -> int:
        return len(self._columns)

    def __contains__(self, key: object) -> bool:
        return key in self._columns_by_name

    @property
    def ids(self) -> Optional[List[ColumnMetadata]]:
        """Get metadata for ID columns used in enrichment responses.

        Returns
        -------
        Optional[List[ColumnMetadata]]
            Metadata for the ID columns, or None if no ID columns exist.
        """
        return self.groups.get(AttributeGroup.ID_ATTRIBUTE_GROUP_NAME)

    @property
    def id_names(self) -> Optional[List[str]]:
        """Get the names of ID columns used in enrichment responses.

        Returns
        -------
        Optional[List[str]]
            Names of the ID columns, or None if no ID columns exist.
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
        return self._groups

    @property
    def columns(self) -> List[ColumnMetadata]:
        """Returns a list of all column metadata objects.

        Returns
        -------
        List[ColumnMetadata]
            A list of all column metadata objects.
        """
        return self._columns
