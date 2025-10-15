from typing import List

from pandas import DataFrame

from cadenzaanalytics.data.column_metadata import ColumnMetadata
from cadenzaanalytics.response.csv_response import CsvResponse


class EnrichmentResponse(CsvResponse):
    """A class representing a enrichment response from an extension.

    Parameters
    ----------
    CsvResponse : type
        The data response type from which EnrichmentResponse inherits.
    """
    def __init__(self, data: DataFrame, column_metadata: List[ColumnMetadata]):
        super().__init__(data, column_metadata)