from typing import List

from cadenzaanalytics.data.attribute_group import AttributeGroup
from cadenzaanalytics.data.data_object import DataObject
from cadenzaanalytics.data.extension_type import ExtensionType
from cadenzaanalytics.data.parameter import Parameter


class AnalyticsExtension(DataObject):
    """Internal data model representing an analytics extension configuration.

    Contains the extension's display name, type, attribute groups, and parameters
    for serialization to JSON when responding to capability requests.
    """
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
        """Get the print name of the analytics extension.

        Returns
        -------
        str
            The print name of the analytics extension.
        """
        return self._print_name

    @property
    def extension_type(self) -> ExtensionType:
        """Get the extension type of the analytics extension.

        Returns
        -------
        ExtensionType
            The extension type of the analytics extension.
        """
        return self._extension_type
