from enum import Enum
from typing import Any

import pandas as pd

# pylint: disable=duplicate-code
class DataType(Enum):
    """Enumeration of supported data types for columns in analytics extensions.

    STRING
        Text/string data.
    INT64
        64-bit integer numbers.
    FLOAT64
        64-bit floating-point numbers.
    ZONEDDATETIME
        Date and time with timezone information.
    GEOMETRY
        Geometric/spatial data.
    """

    STRING = "string"
    INT64 = "int64"
    FLOAT64 = "float64"
    ZONEDDATETIME = "zonedDateTime"
    GEOMETRY = "geometry"

    def __str__(self) -> str:
        return self.value

    def pandas_type(self) -> str:
        """Return the corresponding pandas data type for this DataType.

        Returns
        -------
        str
            The pandas dtype string (e.g., "Int64", "Float64", "string").
        """
        if self.value == 'int64':
            return "Int64"
        if self.value == 'float64':
            return "Float64"
        # geometry columns and zonedDateTime columns are processed afterward and are first parsed as strings
        return "string"

    @classmethod
    def from_pandas_dtype(cls, dtype: Any) -> "DataType":
        """Convert a pandas dtype to the corresponding DataType.

        Parameters
        ----------
        dtype : Any
            A pandas dtype object (e.g., from DataFrame.dtypes).

        Returns
        -------
        DataType
            The corresponding DataType enum member.

        Notes
        -----
        Geometry columns cannot be automatically detected from pandas dtypes
        and will default to STRING. Use explicit ColumnMetadata for geometry columns.
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
