from typing import List

from cadenzaanalytics.data.attribute_group import AttributeGroup


class Table:
    """Defines the structure and expected attributes of input data for an analytics extension."""

    def __init__(self, *,
                 name: str,
                 attribute_groups: List[AttributeGroup]) -> None:
        """Initialize a Table.

        Parameters
        ----------
        name : str
            The name of the table, used to reference it in the analytics request.
        attribute_groups : List[AttributeGroup]
            List of attribute groups defining the expected data structure.
        """
        self._name = name
        self._attribute_groups = attribute_groups

    @property
    def name(self) -> str:
        """Get the name of the table.

        Returns
        -------
        str
            The table name.
        """
        return self._name

    @property
    def attribute_groups(self) -> List[AttributeGroup]:
        """Get the attribute groups of the table.

        Returns
        -------
        List[AttributeGroup]
            The attribute groups defining the table structure.
        """
        return self._attribute_groups
