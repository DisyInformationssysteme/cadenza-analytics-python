import json
from typing import List, Optional, Union

from flask import Response
from requests_toolbelt import MultipartEncoder

from cadenzaanalytics.data.column_metadata import ColumnMetadata
from cadenzaanalytics.data.data_container_metadata import DataContainerMetadata
from cadenzaanalytics.response.extension_response import ExtensionResponse


# pylint: disable=protected-access
class ExtensionDataResponse(ExtensionResponse):
    """Base class for data responses from an analytics extension.

    Handles multipart response encoding with metadata and content.
    """

    def __init__(self, content_type: str, data_container_name: str = 'response-data') -> None:
        """Initialize an ExtensionDataResponse.

        Parameters
        ----------
        content_type : str
            MIME type of the response content (e.g., 'text/csv', 'image/png').
        data_container_name : str, optional
            Name of the data container in the multipart response, by default 'response-data'.
        """
        self._content_type = content_type
        self._data_container_name = data_container_name

    def _get_response_metadata(self, column_metadata: Optional[List[ColumnMetadata]]) -> str:
        metadata = DataContainerMetadata(self._content_type, self._data_container_name, column_metadata)

        # TODO: refactor: utilize message metadata class
        metadata = {
            "dataContainers": [
                metadata._to_dict()
            ]
        }

        return json.dumps(metadata, default=str)

    def _create_response(self, data: Union[str, bytes],
                         column_metadata: Optional[List[ColumnMetadata]] = None) -> Response:
        multipart_response = MultipartEncoder(
            {'metadata': (None, self._get_response_metadata(column_metadata), 'application/json'),
             self._data_container_name: (None, data, self._content_type)}
        )

        return Response(multipart_response.to_string(), mimetype=multipart_response.content_type)
