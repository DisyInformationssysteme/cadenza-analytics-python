from enum import Enum


class GeometryType(Enum):
    POINT = "point"
    LINESTRING = "linestring"
    POLYGON = "polygon"
    MULTIPOINT = "multipoint"
    MULTILINESTRING = "multilinestring"
    MULTIPOLYGON = "multipolygon"

    def __str__(self):
        return self.value
