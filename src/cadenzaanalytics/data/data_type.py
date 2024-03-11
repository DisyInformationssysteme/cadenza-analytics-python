from enum import Enum


# pylint: disable=duplicate-code
class DataType(Enum):
    """A class representing various data types such as string, integer, float, zonedDateTime, and geometry.
    """   
    STRING = "string"
    INT64 = "int64"
    FLOAT64 = "float64"
    ZONEDDATETIME = "zonedDateTime"
    GEOMETRY = "geometry"

    def __str__(self):
        return self.value

    def pandas_type(self):
        """Return the corresponding pandas data type for the given value.

        Returns
        -------
        str
            The pandas data type corresponding to the given value.
        """        
        if self.value == 'int64':
            return "Int64"
        if self.value == 'float64':
            return "Float64"
        return "string"
