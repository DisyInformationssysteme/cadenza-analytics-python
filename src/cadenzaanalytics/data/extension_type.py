from enum import Enum


class ExtensionType(Enum):
    """A class representing the different types of extensions such as visual, enrichment, data.
    """
    VISUAL = "visualization"
    ENRICHMENT = "enrichment"
    DATA = "calculation"

    def __str__(self):
        return self.value
