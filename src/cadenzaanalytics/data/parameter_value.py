from datetime import datetime
from typing import Any, Optional
from shapely import wkt as shapely_wkt

from cadenzaanalytics.data.data_type import DataType
from cadenzaanalytics.data.geometry_type import GeometryType
from cadenzaanalytics.data.data_object import DataObject


class ParameterValue(DataObject):
    """A class representing parameter values as received from cadenza such as name, print_name, parameter_type, value.

    Parameters
    ----------
    DataObject : type
        The base data object type from which Parameter inherits.
    """
    _attribute_mapping = {
        "name": "_name",
        "printName": "_print_name",
        "dataType": "_data_type",
        "value": "_value",
        "geometryType": "_geometry_type",
        "srs": "_srs"
    }
    _attribute_constructors = {
        "dataType": DataType,
        "geometryType": GeometryType
    }

    def __init__(self, *,
                 name: str,
                 print_name: str,
                 data_type: DataType,
                 value: Any = None,
                 geometry_type: GeometryType = None,
                 srs: str = None):
        self._name = name
        self._print_name = print_name
        self._data_type = data_type
        self._value = self._parse_value(value, data_type)
        self._geometry_type = geometry_type
        self._srs = srs


    @property
    def name(self) -> str:
        """Get the name of the parameter.

        Returns
        -------
        str
            The name of the parameter.
        """
        return self._name

    @property
    def print_name(self) -> str:
        """Get the print name of the parameter.

        Returns
        -------
        str
            The print name of the parameter.
        """
        return self._print_name

    @property
    def data_type(self) -> DataType:
        """Get the data type of the parameter.

        Returns
        -------
        DataType
            The data type of the parameter.
        """
        return self._data_type

    @property
    def value(self) -> Any:
        """Get the typed value of the parameter.

        Returns
        -------
        Any
            The value of the parameter, typed according to the data type.
        """
        return self._value

    @property
    def geometry_type(self) -> Optional[GeometryType]:
        """Get the geometry type of the parameter.

        Returns
        -------
        GeometryType
            The geometry type of the parameter.
        """
        return self._geometry_type

    @property
    def srs(self) -> Optional[str]:
        """Get the srs of the parameter."""
        return self._srs


    def _parse_value(self, value: Any, data_type: DataType) -> Any:
        if value is None:
            return None
        if data_type == DataType.INT64:
            return int(value)
        if data_type == DataType.FLOAT64:
            return float(value)
        if data_type == DataType.ZONEDDATETIME:
            return datetime.fromisoformat(value)
        if data_type == DataType.GEOMETRY:
            return shapely_wkt.loads(value)
        return value # retain string and boolean which are already typed correctly