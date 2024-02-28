from typing import List

from cadenzaanalytics.data.attribute_group import AttributeGroup
from cadenzaanalytics.data.data_object import DataObject
from cadenzaanalytics.data.extension_type import ExtensionType
from cadenzaanalytics.data.parameter import Parameter


class AnalyticsExtension(DataObject):
    _attribute_mapping = {
        "printName": "_print_name",
        "extensionType": "_extension_type",
        "attributeGroups": "_attribute_groups",
        "parameters": "_parameters"
    }

    def __init__(self,
                 print_name: str,
                 extension_type: ExtensionType,
                 attribute_groups: List[AttributeGroup],
                 parameters: List[Parameter] = None):
        self._print_name = print_name
        self._extension_type = extension_type
        self._attribute_groups = attribute_groups
        self._parameters = parameters

    @property
    def print_name(self) -> str:
        return self._print_name

    @property
    def extension_type(self) -> ExtensionType:
        return self._extension_type
