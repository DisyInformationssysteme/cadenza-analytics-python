from enum import Enum


class MeasureAggregation(Enum):
    COUNT = "count"
    COUNT_DISTINCT = "countDistinct"
    SUM = "sum"
    AVERAGE = "average"
    MIN = "min"
    MAX = "max"

    def __str__(self):
        return self.value
