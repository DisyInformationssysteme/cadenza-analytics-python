from typing import List, Optional

from cadenzaanalytics.data.data_object import DataObject
from cadenzaanalytics.data.data_type import DataType
from cadenzaanalytics.data.geometry_type import GeometryType


class AttributeGroup(DataObject):
    """Defines a group of attributes with common characteristics for input data.

    Attribute groups specify accepted data types, cardinality constraints, and
    optionally geometry types and spatial reference system for data columns.
    """

    ID_ATTRIBUTE_GROUP_NAME = 'net.disy.cadenza.keyAttributeGroup'

    _attribute_mapping = {
        "name": "_name",
        "printName": "_print_name",
        "dataTypes": "_data_types",
        "geometryTypes": "_geometry_types",
        "requestedSrs": "_requested_srs",
        "minAttributes": "_min_attributes",
        "maxAttributes": "_max_attributes"
    }

    def __init__(self, *,
                 name: str,
                 print_name: str,
                 data_types: List[DataType],
                 geometry_types: Optional[List[GeometryType]] = None,
                 requested_srs: Optional[str] = None,
                 min_attributes: int = 0,
                 max_attributes: Optional[int] = None) -> None:
        """Initialize an AttributeGroup.

        Parameters
        ----------
        name : str
            Internal name of the attribute group.
        print_name : str
            User-friendly display name of the attribute group.
        data_types : List[DataType]
            List of accepted data types for this attribute group.
        geometry_types : Optional[List[GeometryType]], optional
            List of accepted geometry types, required for geometry data types.
        requested_srs : Optional[str], optional
            Requested spatial reference system for geometry columns.
        min_attributes : int, optional
            Minimum number of attributes required, by default 0.
        max_attributes : Optional[int], optional
            Maximum number of attributes allowed, None means unlimited.
        """
        self._name = name
        self._print_name = print_name
        self._data_types = data_types
        self._geometry_types = geometry_types
        self._requested_srs = requested_srs
        self._min_attributes = min_attributes
        self._max_attributes = max_attributes
