from enum import Enum


class AttributeRole(Enum):
    """A class representing attribute roles in data modeling like dimension and measure.
    """
    DIMENSION = "dimension"
    MEASURE = "measure"

    def __str__(self):
        return self.value
