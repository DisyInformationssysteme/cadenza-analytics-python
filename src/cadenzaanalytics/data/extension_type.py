from enum import Enum


class ExtensionType(Enum):
    """A class representing the different types of extensions such as visualization, enrichment, calculation.
    """    
    VISUALIZATION = "visualization"
    ENRICHMENT = "enrichment"
    CALCULATION = "calculation"

    def __str__(self):
        return self.value
