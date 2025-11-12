from typing import List

from pandas import DataFrame

from cadenzaanalytics.data.column_metadata import ColumnMetadata
from cadenzaanalytics.response.csv_response import CsvResponse
from cadenzaanalytics.response.missing_metadata_strategy import MissingMetadataStrategy


class CalculationResponse(CsvResponse):
    """A class representing a calculation response from an extension.

    Parameters
    ----------
    CsvResponse : type
        The data response type from which CalculationResponse inherits.
    """
    def __init__(self, data: DataFrame, column_metadata: List[ColumnMetadata], missing_metadata_strategy: MissingMetadataStrategy = MissingMetadataStrategy.ADD_DEFAULT_METADATA):
        super().__init__(data, column_metadata, missing_metadata_strategy)