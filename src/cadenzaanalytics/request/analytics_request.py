from cadenzaanalytics.request.request_parameter import RequestParameter
from cadenzaanalytics.request.request_table import RequestTable
from cadenzaanalytics.request.request_metadata import RequestMetadata


class AnalyticsRequest:
    """A class representing an analytics request.
    """
    def __init__(self, metadata: RequestMetadata):
        # TODO: Refactor
        self._request_parameter = RequestParameter(metadata)
        self._tables = {}

    def __getitem__(self, key) -> RequestTable:
        """Returns the request table object by name.

        Parameters
        ----------
        key : str
            The name of the request table.

        Returns
        -------
        RequestTable
            Request table with the name provided as key parameter.
        """

        return self._tables[key]


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
