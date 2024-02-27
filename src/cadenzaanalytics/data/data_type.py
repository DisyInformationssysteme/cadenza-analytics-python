from enum import Enum


# pylint: disable=duplicate-code
class DataType(Enum):
    STRING = "string"
    INT64 = "int64"
    FLOAT64 = "float64"
    ZONEDDATETIME = "zonedDateTime"
    GEOMETRY = "geometry"

    def __str__(self):
        return self.value

    def pandas_type(self):
        if self.value == 'int64':
            return "Int64"
        if self.value == 'float64':
            return "Float64"
        return "string"
