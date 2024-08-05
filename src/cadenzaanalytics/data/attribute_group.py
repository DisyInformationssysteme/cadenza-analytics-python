from typing import List

from cadenzaanalytics.data.data_object import DataObject
from cadenzaanalytics.data.data_type import DataType


KEY_ATTRIBUTE_GROUP_NAME = 'net.disy.cadenza.keyAttributeGroup'


class AttributeGroup(DataObject):
    """A class representing a group of attributes such as name, print_name, data_types, geometry_types,
     min_attributes and max_attributes.

    Parameters
    ----------
    DataObject : type
        The base data object type from which AttributeGroup inherits.
    """
    _attribute_mapping = {
        "name": "_name",
        "printName": "_print_name",
        "dataTypes": "_data_types",
        "geometryTypes": "_geometry_types",
        "minAttributes": "_min_attributes",
        "maxAttributes": "_max_attributes"
    }

    def __init__(self,
                 name: str,
                 print_name: str,
                 data_types: List[DataType],
                 geometry_types: List = None,
                 min_attributes: int = 0,
                 max_attributes: int = None):
        self._name = name
        self._print_name = print_name
        self._data_types = data_types
        self._geometry_types = geometry_types
        self._min_attributes = min_attributes
        self._max_attributes = max_attributes
