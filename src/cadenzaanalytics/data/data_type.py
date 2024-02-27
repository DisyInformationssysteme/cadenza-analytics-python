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
