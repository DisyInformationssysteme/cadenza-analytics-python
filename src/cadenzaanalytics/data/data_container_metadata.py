from typing import List

from cadenzaanalytics.data.column_metadata import ColumnMetadata
from cadenzaanalytics.data.data_object import DataObject


class DataContainerMetadata(DataObject):
    """A class representing metadata for data containers such as type, name and columns.

    Parameters
    ----------
    DataObject : type
        The base data object type from which DataContainerMetadata inherits.
    """
    _attribute_mapping = {
        "type": "_content_type",
        "name": "_name",
        "columns": "_columns"
    }

    def __init__(self, content_type: str, name: str, columns: List[ColumnMetadata] = None):
        self._content_type = content_type
        self._name = name
        self._columns = columns
