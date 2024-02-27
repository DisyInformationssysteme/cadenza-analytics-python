from enum import Enum


class AttributeRole(Enum):
    DIMENSION = "dimension"
    MEASURE = "measure"

    def __str__(self):
        return self.value
