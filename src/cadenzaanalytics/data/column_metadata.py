from typing import Optional

from cadenzaanalytics.data.geometry_type import GeometryType
from cadenzaanalytics.data.attribute_role import AttributeRole
from cadenzaanalytics.data.data_object import DataObject
from cadenzaanalytics.data.data_type import DataType
from cadenzaanalytics.data.measure_aggregation import MeasureAggregation


# pylint: disable=too-many-instance-attributes
class ColumnMetadata(DataObject):
    """Metadata describing a column in request or response data.

    Defines properties such as name, data type, role, and formatting for a data column.
    Used both for describing incoming request data and specifying response column properties.
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
                 role: Optional[AttributeRole] = None,
                 attribute_group_name: str = "data",
                 measure_aggregation: Optional[MeasureAggregation] = None,
                 format: Optional[str] = None,
                 geometry_type: Optional[GeometryType] = None,
                 srs: Optional[str] = None) -> None:
        """Initialize ColumnMetadata.

        Parameters
        ----------
        name : str
            Internal column name, must match the DataFrame column name.
        print_name : str
            User-friendly display name for the column.
        data_type : DataType
            The data type of the column.
        role : Optional[AttributeRole], optional
            The role of the column (e.g., dimension, measure).
        attribute_group_name : str, optional
            Name of the attribute group this column belongs to, by default "data".
        measure_aggregation : Optional[MeasureAggregation], optional
            Aggregation method for measure columns.
        format : Optional[str], optional
            Display format string for the column.
        geometry_type : Optional[GeometryType], optional
            Geometry type for geometry columns.
        srs : Optional[str], optional
            Spatial reference system for geometry columns.
        """
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
    def role(self) -> Optional[AttributeRole]:
        """Get the role of the column.

        ColumnMetadata received from Cadenza will always have a role set.
        For user-created metadata, the role may be None if not specified.

        Returns
        -------
        Optional[AttributeRole]
            The role of the column, or None if not specified.
        """
        return self._role

    @property
    def measure_aggregation(self) -> Optional[MeasureAggregation]:
        """Get the measure aggregation of the column.

        Returns
        -------
        Optional[MeasureAggregation]
            The measure aggregation of the column, or None if not specified.
        """
        return self._measure_aggregation

    @property
    def format(self) -> Optional[str]:
        """Get the format of the column.

        Returns
        -------
        Optional[str]
            The display format string for the column, or None if not specified.
        """
        return self._format

    @property
    def geometry_type(self) -> Optional[GeometryType]:
        """Get the geometry type of the column.

        Returns
        -------
        Optional[GeometryType]
            The geometry type of the column, or None for non-geometry columns.
        """
        return self._geometry_type

    @property
    def srs(self) -> Optional[str]:
        """Get the spatial reference system (SRS) of the column.

        Returns
        -------
        Optional[str]
            The SRS of the column, or None if not specified.
        """
        return self._srs
