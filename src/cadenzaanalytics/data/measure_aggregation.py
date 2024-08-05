from enum import Enum


class MeasureAggregation(Enum):
    """A class representing various aggregation functions for measures such as count, countDistinct,
    sum, average, min and max.
    """
    COUNT = "count"
    COUNT_DISTINCT = "countDistinct"
    SUM = "sum"
    AVERAGE = "average"
    MIN = "min"
    MAX = "max"

    def __str__(self):
        return self.value
