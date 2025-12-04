from pandas import DataFrame

from cadenzaanalytics.request.request_metadata import RequestMetadata


class RequestTable:
    """Represents a data table within an analytics request.

    Contains the actual data as a pandas DataFrame and metadata describing the columns.
    """

    def __init__(self, data: DataFrame, metadata: RequestMetadata) -> None:
        """Initialize a RequestTable.

        Parameters
        ----------
        data : DataFrame
            The data payload as a pandas DataFrame.
        metadata : RequestMetadata
            Metadata describing the columns in the data.
        """
        self._data = data
        self._metadata = metadata

    @property
    def metadata(self) -> RequestMetadata:
        """Get the metadata associated with the table.

        Returns
        -------
        RequestMetadata
            Metadata describing the columns and their properties.
        """
        return self._metadata

    @property
    def data(self) -> DataFrame:
        """Get the data payload of the table.

        Returns
        -------
        DataFrame
            The table data as a pandas DataFrame.
        """
        return self._data
