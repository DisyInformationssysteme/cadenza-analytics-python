from enum import Enum


class ParameterType(Enum):
    """Enumeration of supported parameter types for analytics extensions.

    STRING
        Text input parameter.
    INT64
        Integer number parameter.
    FLOAT64
        Floating-point number parameter.
    ZONEDDATETIME
        Date and time with timezone parameter.
    GEOMETRY
        Geometry/location parameter.
    SELECT
        Selection from predefined options.
    BOOLEAN
        True/false parameter.
    """

    STRING = "string"
    INT64 = "int64"
    FLOAT64 = "float64"
    ZONEDDATETIME = "zonedDateTime"
    GEOMETRY = "geometry"
    SELECT = "select"
    BOOLEAN = "boolean"

    def __str__(self) -> str:
        return self.value
