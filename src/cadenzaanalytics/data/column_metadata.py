from typing import Optional

from cadenzaanalytics.data.geometry_type import GeometryType
from cadenzaanalytics.data.attribute_role import AttributeRole
from cadenzaanalytics.data.data_object import DataObject
from cadenzaanalytics.data.data_type import DataType
from cadenzaanalytics.data.measure_aggregation import MeasureAggregation


# pylint: disable=too-many-instance-attributes
class ColumnMetadata(DataObject):
    """A class representing metadata for columns such as the name, print_name, attribute_group_name, data_type, role,
     measure_aggregation, format and geometry_type.

    Parameters
    ----------
    DataObject : type
        The base data object type from which ColumnMetadata inherits.

    Returns
    -------
    type
        Description of what the method returns.
    """
    _attribute_mapping = {
        "name": "_name",
        "printName": "_print_name",
        "attributeGroupName": "_attribute_group_name",
        "dataType": "_data_type",
        "role": "_role",
        "measureAggregation": "_measure_aggregation",
        "format": "_format",
        "geometryType": "_geometry_type",
        "srs": "_srs"
    }
    _attribute_constructors = {
        "dataType": DataType,
        "role": AttributeRole,
        "measureAggregation": MeasureAggregation,
        "geometryType": GeometryType
    }

    # pylint: disable=redefined-builtin, too-many-arguments
    def __init__(self, *,
                 name: str,
                 print_name: str,
                 data_type: DataType,
                 role: AttributeRole = None,
                 attribute_group_name: str = "data",
                 measure_aggregation: MeasureAggregation = None,
                 format: str = None,
                 geometry_type: GeometryType = None,
                 srs: str = None):
        self._name = name
        self._print_name = print_name
        self._attribute_group_name = attribute_group_name
        self._data_type = data_type
        self._role = role
        self._measure_aggregation = measure_aggregation
        self._format = format
        self._geometry_type = geometry_type
        self._srs = srs

    @property
    def name(self) -> str:
        """Get the name of the column.

        Returns
        -------
        str
            The name of the column.
        """
        return self._name

    @property
    def print_name(self) -> str:
        """Get the print name of the column.

        Returns
        -------
        str
            The print name of the column.
        """
        return self._print_name

    @property
    def attribute_group_name(self) -> str:
        """Get the attribute group name of the column.

        Returns
        -------
        str
            The attribute group name of the column.
        """
        return self._attribute_group_name

    @property
    def data_type(self) -> DataType:
        """Get the data type of the column.

        Returns
        -------
        DataType
            The data type of the column.
        """
        return self._data_type

    @property
    def role(self) -> AttributeRole:
        """Get the role of the column. ColumnMetadata received from cadenza will always have a role set.

        Returns
        -------
        AttributeRole
            The role of the column.
        """
        return self._role

    @property
    def measure_aggregation(self) -> Optional[MeasureAggregation]:
        """Get the measure aggregation of the column.

        Returns
        -------
        MeasureAggregation
            The measure aggregation of the column.
        """
        return self._measure_aggregation

    @property
    def format(self) -> Optional[str]:
        """Get the format of the column.

        Returns
        -------
        str
            The format of the column.
        """
        return self._format

    @property
    def geometry_type(self) -> Optional[GeometryType]:
        """Get the geometry type of the column.

        Returns
        -------
        GeometryType
            The geometry type of the column.
        """
        return self._geometry_type

    @property
    def srs(self) -> Optional[str]:
        """Get the srs of the column."""
        return self._srs
