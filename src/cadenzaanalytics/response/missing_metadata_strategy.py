from enum import Enum


class MissingMetadataStrategy(Enum):
    """A class representing the strategies to handle missing metadata for enrichment and data responses.
    """
    ADD_DEFAULT_METADATA = "add_default_metadata"
    REMOVE_DATA_COLUMNS = "remove_data_columns"
    RAISE_EXCEPTION = "raise_exception"

    def __str__(self):
        return self.value
