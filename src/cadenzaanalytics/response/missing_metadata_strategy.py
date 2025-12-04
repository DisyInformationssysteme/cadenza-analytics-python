from enum import Enum


class MissingMetadataStrategy(Enum):
    """Strategy for handling DataFrame columns without explicit metadata definitions.

    ADD_DEFAULT_METADATA
        Generate default metadata based on pandas dtype for columns without metadata.
    REMOVE_DATA_COLUMNS
        Remove columns from the response if they have no metadata definition.
    RAISE_EXCEPTION
        Raise a ValueError if any column lacks metadata.
    """

    ADD_DEFAULT_METADATA = "add_default_metadata"
    REMOVE_DATA_COLUMNS = "remove_data_columns"
    RAISE_EXCEPTION = "raise_exception"

    def __str__(self) -> str:
        return self.value
