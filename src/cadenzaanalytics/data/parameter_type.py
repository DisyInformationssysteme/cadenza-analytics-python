from enum import Enum


class ParameterType(Enum):
    STRING = "string"
    INT64 = "int64"
    FLOAT64 = "float64"
    ZONEDDATETIME = "zonedDateTime"
    GEOMETRY = "geometry"
    SELECT = "select"
    BOOLEAN = "boolean"
