from cadenzaanalytics.request.request_metadata import RequestMetadata
from cadenzaanalytics.request.request_parameter import RequestParameter


class AnalyticsRequest:
    """A class representing an analytics request.
    """
    def __init__(self, metadata: RequestMetadata):
        # TODO: Refactor
        self._request_parameter = RequestParameter(self.metadata)
        self._tables = {}

    @property
    def parameters(self) -> RequestParameter:
        """Get the parameter associated with the request.

        Returns
        -------
        RequestParameter
            The parameters associated with the request.
        """
        return self._request_parameter

    def add_request_table(self, name: str, metadata: RequestMetadata, data):
        """Add request table to the analytics request"""

        self._tables[name] = RequestTable(metadata=metadata, data=data)
