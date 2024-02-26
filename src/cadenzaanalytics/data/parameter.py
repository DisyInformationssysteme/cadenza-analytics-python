from cadenzaanalytics.data.data_object import DataObject
from cadenzaanalytics.data.parameter_type import ParameterType


class Parameter(DataObject):
    _attribute_mapping = {
        "name": "_name",
        "printName": "_print_name",
        "parameterType": "_parameter_type",
        "options": "_options",
        "required": "_required",
        "defaultValue": "_default_value"
    }

    def __init__(self,
                 name: str,
                 print_name: str,
                 parameter_type: ParameterType,
                 options: list[str] = None,
                 required: bool = False,
                 default_value: any = None):
        self._name = name
        self._print_name = print_name
        self._parameter_type = parameter_type
        self._options = options
        self._required = required
        self._default_value = default_value
