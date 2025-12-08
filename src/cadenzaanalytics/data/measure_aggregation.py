from enum import Enum


class MeasureAggregation(Enum):
    """A class representing various aggregation functions for measures such as count, count distinct,
    sum, average, min, max, median and sample standard deviation.
    """
    COUNT = "count"
    COUNT_DISTINCT = "countDistinct"
    SUM = "sum"
    AVERAGE = "average"
    MIN = "min"
    MAX = "max"
    MEDIAN = "median"
    STANDARD_DEVIATION_SAMPLE = "stddevSamp"

    def __str__(self):
        return self.value
