from cadenzaanalytics.request.request_metadata import RequestMetadata


class AnalyticsRequest:
    """A class representing an analytics request.
    """
    def __init__(self, metadata: RequestMetadata, data):
        self._metadata = metadata
        self._data = data

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
    def data(self):
        """Get the data payload of the request.

        Returns
        -------
        object
            The data associated with the request.
        """
        return self._data
