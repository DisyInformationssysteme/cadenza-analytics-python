from typing import List, Any

from cadenzaanalytics.data.geometry_type import GeometryType
from cadenzaanalytics.data.data_object import DataObject
from cadenzaanalytics.data.parameter_type import ParameterType


# pylint: disable=too-many-instance-attributes
class Parameter(DataObject):
    """A class representing parameters such as name, print_name, parameter_type, options, required
    and default_value used in data objects.

    Parameters
    ----------
    DataObject : type
        The base data object type from which Parameter inherits.
    """
    _attribute_mapping = {
        "name": "_name",
        "printName": "_print_name",
        "parameterType": "_parameter_type",
        "geometryTypes": "_geometry_types",
        "options": "_options",
        "required": "_required",
        "defaultValue": "_default_value",
        "requestedSrs": "_requested_srs"
    }

    def __init__(self, *,
                 name: str,
                 print_name: str,
                 parameter_type: ParameterType,
                 geometry_types: List[GeometryType] = None,
                 options: List[str] = None,
                 required: bool = False,
                 default_value: Any = None,
                 requested_srs: str = None):
        self._name = name
        self._print_name = print_name
        self._parameter_type = parameter_type
        self._geometry_types = geometry_types
        self._options = options
        self._required = required
        self._default_value = default_value
        self._requested_srs = requested_srs
