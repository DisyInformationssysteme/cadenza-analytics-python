from typing import List

from cadenzaanalytics.data.attribute_group import AttributeGroup


class Table:
    def __init__(self,  *,
                 name: str,
                 attribute_groups: List[AttributeGroup]):
        self._name = name
        self._attribute_groups = attribute_groups

    @property
    def name(self) -> str:
        """Get the name of the table."""
        return self._name

    @property
    def attribute_groups(self) -> List[AttributeGroup]:
        """Get the attribute groups of the table."""
        return self._attribute_groups
