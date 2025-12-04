from typing import List

from pandas import DataFrame

from cadenzaanalytics.data.column_metadata import ColumnMetadata
from cadenzaanalytics.response.csv_response import CsvResponse
from cadenzaanalytics.response.missing_metadata_strategy import MissingMetadataStrategy


class DataResponse(CsvResponse):
    """A response containing new data from an analytics extension.

    Use this response type for DATA extensions that return entirely new data
    rather than enriching existing data.
    """

    def __init__(self,
                 data: DataFrame,
                 column_metadata: List[ColumnMetadata],
                 *,
                 missing_metadata_strategy: MissingMetadataStrategy = MissingMetadataStrategy.ADD_DEFAULT_METADATA
                 ) -> None:
        """Initialize a DataResponse.

        Parameters
        ----------
        data : DataFrame
            The response data as a pandas DataFrame.
        column_metadata : List[ColumnMetadata]
            Metadata describing the columns in the response.
        missing_metadata_strategy : MissingMetadataStrategy, optional
            Strategy for handling columns without metadata,
            by default ADD_DEFAULT_METADATA.
        """
        super().__init__(data, column_metadata, missing_metadata_strategy=missing_metadata_strategy)
