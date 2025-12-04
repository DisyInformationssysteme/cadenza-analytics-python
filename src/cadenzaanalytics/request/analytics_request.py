import collections
from typing import Iterator, Optional

from cadenzaanalytics.request.request_parameter import RequestParameter
from cadenzaanalytics.request.request_table import RequestTable


class AnalyticsRequest(collections.abc.Mapping):
    """Represents an incoming analytics request from Cadenza.

    Provides access to request parameters and data tables. Supports dict-like
    access to tables via `request["table_name"]` syntax.
    """

    def __init__(self, parameters: RequestParameter, cadenza_version: str) -> None:
        """Initialize an AnalyticsRequest.

        Parameters
        ----------
        parameters : RequestParameter
            The request parameters provided by Cadenza.
        cadenza_version : str
            Version string of the Cadenza instance sending the request.
        """
        self._parameters = parameters
        self._tables = {}
        self._cadenza_version = cadenza_version

    def __getitem__(self, key: str) -> RequestTable:
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

    def __iter__(self) -> Iterator[str]:
        return iter(self._tables)

    def __len__(self) -> int:
        return len(self._tables)

    def __setitem__(self, name: str, request_table: RequestTable) -> None:
        self._tables[name] = request_table

    @property
    def parameters(self) -> RequestParameter:
        """Get the parameters associated with the request.

        Returns
        -------
        RequestParameter
            The parameters provided by Cadenza.
        """
        return self._parameters

    @property
    def cadenza_version(self) -> Optional[str]:
        """Get the Cadenza version that sent the request.

        Returns
        -------
        Optional[str]
            The Cadenza version string, or None if not provided.
        """
        return self._cadenza_version
