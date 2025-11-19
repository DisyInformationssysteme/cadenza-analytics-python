from enum import Enum


class ExtensionType(Enum):
    """A class representing the different types of extensions such as visual, enrichment, data.
    """
    VISUAL = "visual"
    ENRICHMENT = "enrichment"
    DATA = "data"

    def __str__(self):
        return self.value
