from enum import Enum


class ParameterType(Enum):
    """A class representing parameter types.

    Returns
    -------
    str
        A string representing the parameter type.
    """    
    STRING = "string"
    INT64 = "int64"
    FLOAT64 = "float64"
    ZONEDDATETIME = "zonedDateTime"
    GEOMETRY = "geometry"
    SELECT = "select"
    BOOLEAN = "boolean"

    def __str__(self):
        return self.value
