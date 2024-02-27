from enum import Enum


class ExtensionType(Enum):
    VISUALIZATION = "visualization"
    ENRICHMENT = "enrichment"
    CALCULATION = "calculation"

    def __str__(self):
        return self.value
