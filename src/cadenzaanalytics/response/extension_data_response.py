import json

from flask import Response
from requests_toolbelt import MultipartEncoder

from cadenzaanalytics.data.data_container_metadata import DataContainerMetadata
from cadenzaanalytics.response.extension_response import ExtensionResponse


# pylint: disable=protected-access
class ExtensionDataResponse(ExtensionResponse):
    def __init__(self, content_type, data_container_name='response-data'):
        self._content_type = content_type
        self._data_container_name = data_container_name

    def _get_response_metadata(self, column_metadata):
        metadata = DataContainerMetadata(self._content_type, self._data_container_name, column_metadata)

        # TODO: refactor: utilize message metadata class
        metadata = {
            "dataContainers": [
                metadata._to_dict()
            ]
        }

        return json.dumps(metadata)

    def _create_response(self, data, column_metadata=None):
        multipart_response = MultipartEncoder(
            {'metadata': (None, self._get_response_metadata(column_metadata), 'application/json'),
             self._data_container_name: (None, data, self._content_type)}
        )

        return Response(multipart_response.to_string(), mimetype=multipart_response.content_type)
