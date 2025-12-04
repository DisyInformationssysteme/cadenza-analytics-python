import collections

from cadenzaanalytics.request.request_parameter import RequestParameter
from cadenzaanalytics.request.request_table import RequestTable


class AnalyticsRequest(collections.abc.Mapping):
    """A class representing an analytics request.
    """
    def __init__(self, parameters: RequestParameter, cadenza_version: str):
        self._parameters = parameters
        self._tables = {}
        self._cadenza_version = cadenza_version

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

    def __contains__(self, table_name: str) -> bool:
        """Check if the request has a table with the provided name."""
        return table_name in self._tables

    def __iter__(self):
        return iter(self._tables)

    def __len__(self):
        return len(self._tables)

    def __setitem__(self, name: str, request_table: RequestTable):
        self._tables[name] = request_table

    @property
    def parameters(self) -> RequestParameter:
        """Get the parameter associated with the request.

        Returns
        -------
        RequestParameter
            The parameters associated with the request.
        """
        return self._parameters

    @property
    def cadenza_version(self) -> str:
        return self._cadenza_version
