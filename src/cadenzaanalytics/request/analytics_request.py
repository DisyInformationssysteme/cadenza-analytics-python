from cadenzaanalytics.request.request_metadata import RequestMetadata


class AnalyticsRequest:
    def __init__(self, metadata: RequestMetadata, data):
        self._metadata = metadata
        self._data = data

    @property
    def metadata(self) -> RequestMetadata:
        return self._metadata

    @property
    def data(self):
        return self._data
