from typing import List, Optional

from cadenzaanalytics.data.geometry_type import GeometryType
from cadenzaanalytics.data.data_object import DataObject
from cadenzaanalytics.data.parameter_type import ParameterType
from cadenzaanalytics.data.parameter_value_type import ParameterValueType


# pylint: disable=too-many-instance-attributes
class Parameter(DataObject):
    """Defines a user-configurable parameter for an analytics extension.

    Parameters allow users to provide input values when running an extension,
    such as thresholds, filters, or configuration options.
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
                 geometry_types: Optional[List[GeometryType]] = None,
                 options: Optional[List[str]] = None,
                 required: bool = False,
                 default_value: Optional[ParameterValueType] = None,
                 requested_srs: Optional[str] = None) -> None:
        """Initialize a Parameter.

        Parameters
        ----------
        name : str
            Internal parameter name, used to access the value in the request.
        print_name : str
            User-friendly display name for the parameter.
        parameter_type : ParameterType
            The data type of the parameter.
        geometry_types : Optional[List[GeometryType]], optional
            Accepted geometry types for GEOMETRY parameters.
        options : Optional[List[str]], optional
            List of allowed values for SELECT parameters.
        required : bool, optional
            Whether the parameter is required, by default False.
            For parameter type boolean, required=True makes submitting the value
            True mandatory.
        default_value : Optional[ParameterValueType], optional
            Default value if the user doesn't provide one.
        requested_srs : Optional[str], optional
            Requested spatial reference system for GEOMETRY parameters.
        """
        self._name = name
        self._print_name = print_name
        self._parameter_type = parameter_type
        self._geometry_types = geometry_types
        self._options = options
        self._required = required
        self._default_value = default_value
        self._requested_srs = requested_srs
