from enum import Enum


class GeometryType(Enum):
    """A class representing different types of geometries such as point, linestring, polygon, multipoint, multilinestring, multipolygon.
    """ 
    POINT = "point"
    LINESTRING = "linestring"
    POLYGON = "polygon"
    MULTIPOINT = "multipoint"
    MULTILINESTRING = "multilinestring"
    MULTIPOLYGON = "multipolygon"

    def __str__(self):
        return self.value
