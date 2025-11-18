from enum import Enum

from pandas import DataFrame

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

    def pandas_type(self) -> str:
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


    @classmethod
    def from_pandas_dtype(cls, dtype: DataFrame.dtypes):
        """Return the cadenza analytics data type for given pandas data type.

        Returns
        -------
        DataType
            The cadenza analytics data type corresponding to the given value.
        """
        if dtype == 'int64':
            return DataType.INT64
        if dtype == 'float64':
            return DataType.FLOAT64
        return DataType.STRING
