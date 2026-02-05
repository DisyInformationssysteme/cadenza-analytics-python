import collections
from typing import Iterator, Optional

from cadenzaanalytics.request.request_parameter import RequestParameter
from cadenzaanalytics.request.request_table import RequestTable


class AnalyticsRequest(collections.abc.Mapping[str, RequestTable]):
    """Represents an incoming analytics request from Cadenza.

    Provides access to request parameters and data tables. Supports dict-like
    access to tables via `request["table_name"]` syntax.
    """

    def __init__(self,
                 parameters: RequestParameter,
                 cadenza_version: str,
                 cadenza_timezone_region: str,
                 cadenza_timezone_current_offset: str) -> None:
        """Initialize an AnalyticsRequest.

        Parameters
        ----------
        parameters : RequestParameter
            The request parameters provided by Cadenza.
        cadenza_version : str
            Version string of the Cadenza instance sending the request.
        cadenza_timezone_region : str
            The timezone region (e.g. "Europe/Berlin") of the Cadenza instance sending the request.
        cadenza_timezone_current_offset : str
            The current timezone offset (e.g. "+01:00") of the Cadenza instance sending the request.
        """
        self._parameters = parameters
        self._tables = {}
        self._cadenza_version = cadenza_version
        self._cadenza_timezone_region = cadenza_timezone_region
        self._cadenza_timezone_current_offset = cadenza_timezone_current_offset

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

    @property
    def cadenza_timezone_region(self):
        """Get the timezone region of the Cadenza instance that sent the request. If (an older version of)
        Cadenza did not send a timezone region, this will be the region of this server.

        :return: Region identifier, such as "Europe/Berlin".
        """
        return self._cadenza_timezone_region

    @property
    def cadenza_timezone_current_offset(self):
        """Get the current timezone offset of the Cadenza instance that sent the request. If (an older version of)
        Cadenza did not send a timezone offset, this will be the offset of this server.
        This information is purely informational and volatile as it will change with the daylight savings time.
        It should not be used to convert datetime objects
        to zone-aware datetimes, for that use the cadenza_timezone_region property.

        :return: Offset string, such as "+01:00" or "Z".
        """
        return self._cadenza_timezone_current_offset
