from pandas import DataFrame

from cadenzaanalytics.request.request_metadata import RequestMetadata


class RequestTable:
    """A class representing an analytics request table.
    """
    def __init__(self, data: DataFrame, metadata: RequestMetadata):
        self._data = data
        self._metadata = metadata

    @property
    def metadata(self) -> RequestMetadata:
        """Get the metadata associated with the request.

        Returns
        -------
        RequestMetadata
            The metadata associated with the request.
        """
        return self._metadata

    @property
    def data(self) -> DataFrame:
        """Get the data payload of the request.

        Returns
        -------
        object
            The data associated with the request.
        """
        return self._data
