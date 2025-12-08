from datetime import datetime
from typing import Any, Optional
from shapely import wkt as shapely_wkt

from cadenzaanalytics.data.data_type import DataType
from cadenzaanalytics.data.geometry_type import GeometryType
from cadenzaanalytics.data.data_object import DataObject
from cadenzaanalytics.data.parameter_value_type import ParameterValueType


class ParameterValue(DataObject):
    """Represents a parameter value received from Cadenza with its metadata.

    Contains the parameter's value along with type information and optional
    geometry metadata for GEOMETRY type parameters.
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
                 geometry_type: Optional[GeometryType] = None,
                 srs: Optional[str] = None) -> None:
        """Initialize a ParameterValue.

        Parameters
        ----------
        name : str
            The internal name of the parameter.
        print_name : str
            The user-friendly display name of the parameter.
        data_type : DataType
            The data type of the parameter value.
        value : Any, optional
            The raw parameter value, will be converted according to data_type.
        geometry_type : Optional[GeometryType], optional
            The geometry type for GEOMETRY parameters.
        srs : Optional[str], optional
            The spatial reference system for GEOMETRY parameters.
        """
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
    def value(self) -> Optional[ParameterValueType]:
        """Get the typed value of the parameter.

        Returns
        -------
        Optional[ParameterValueType]
            The value of the parameter, typed according to the data type.
        """
        return self._value

    @property
    def geometry_type(self) -> Optional[GeometryType]:
        """Get the geometry type of the parameter.

        Returns
        -------
        Optional[GeometryType]
            The geometry type of the parameter, or None for non-geometry parameters.
        """
        return self._geometry_type

    @property
    def srs(self) -> Optional[str]:
        """Get the spatial reference system (SRS) of the parameter.

        Returns
        -------
        Optional[str]
            The SRS specification, or None if not applicable.
        """
        return self._srs


    def _parse_value(self, value: Any, data_type: DataType) -> Optional[ParameterValueType]:
        """Parse and convert a parameter value according to its data type.

        Parameters
        ----------
        value : Any
            The raw value to parse.
        data_type : DataType
            The target data type for conversion.

        Returns
        -------
        Optional[ParameterValueType]
            The parsed value with appropriate type, or None if input is None.
        """
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
        return value  # retain string and boolean which are already typed correctly
