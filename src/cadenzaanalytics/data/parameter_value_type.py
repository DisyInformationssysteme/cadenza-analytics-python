from __future__ import annotations

from datetime import datetime
from typing import Union

from shapely.geometry.base import BaseGeometry

# A typed value for parameters: numbers, strings, boolean, shapely geometries, and datetime
ParameterValueType = Union[int, float, str, bool, datetime, BaseGeometry]
