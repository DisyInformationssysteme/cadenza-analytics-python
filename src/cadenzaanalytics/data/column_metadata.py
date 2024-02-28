from cadenzaanalytics.data.geometry_type import GeometryType
from cadenzaanalytics.data.attribute_role import AttributeRole
from cadenzaanalytics.data.data_object import DataObject
from cadenzaanalytics.data.data_type import DataType
from cadenzaanalytics.data.measure_aggregation import MeasureAggregation


# pylint: disable=too-many-instance-attributes
class ColumnMetadata(DataObject):
    _attribute_mapping = {
        "name": "_name",
        "printName": "_print_name",
        "attributeGroupName": "_attribute_group_name",
        "dataType": "_data_type",
        "role": "_role",
        "measureAggregation": "_measure_aggregation",
        "format": "_format",
        "geometryType": "_geometry_type"
    }
    _attribute_constructors = {
        "dataType": DataType,
        "role": AttributeRole,
        "measureAggregation": MeasureAggregation,
        "geometryType": GeometryType
    }

    # pylint: disable=redefined-builtin
    def __init__(self,
                 name: str,
                 print_name: str,
                 attribute_group_name: str,
                 data_type: DataType,
                 role: AttributeRole,
                 measure_aggregation: MeasureAggregation = None,
                 format: str = None,
                 geometry_type: str = None):
        self._name = name
        self._print_name = print_name
        self._attribute_group_name = attribute_group_name
        self._data_type = data_type
        self._role = role
        self._measure_aggregation = measure_aggregation
        self._format = format
        self._geometry_type = geometry_type

    @property
    def name(self) -> str:
        return self._name

    @property
    def print_name(self) -> str:
        return self._print_name

    @property
    def attribute_group_name(self) -> str:
        return self._attribute_group_name

    @property
    def data_type(self) -> DataType:
        return self._data_type

    @property
    def role(self) -> AttributeRole:
        return self._role

    @property
    def measure_aggregation(self) -> MeasureAggregation | None:
        return self._measure_aggregation

    @property
    def format(self) -> str:
        return self._format

    @property
    def geometry_type(self) -> str:
        return self._geometry_type
