from enum import Enum

import pandas as pd

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
        # geometry columns and zonedDateTime columns are processed afterward and are first parsed as strings
        return "string"


    @classmethod
    def from_pandas_dtype(cls, dtype) -> "DataType":
        """Return the cadenza analytics data type for given pandas data type.

        Returns
        -------
        DataType
            The cadenza analytics data type corresponding to the given value.
        """

        if pd.api.types.is_datetime64_any_dtype(dtype):
            return cls.ZONEDDATETIME

        if pd.api.types.is_integer_dtype(dtype):
            return cls.INT64

        if pd.api.types.is_float_dtype(dtype):
            return cls.FLOAT64

        if pd.api.types.is_string_dtype(dtype) or dtype is object:
            return cls.STRING

        # boolean, categorical, others default to string

        # Geometry also defaults to string: Critical metadata such as GeometryType or coordinate system is not
        # available in a pandas data frame. We cannot assume that we have a geoPandas dataframe, and we should
        # not assume the underlying crs or desired geometry type; thus geometry columns need to be defined by the user.
        return cls.STRING
