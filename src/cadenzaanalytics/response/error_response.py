import json

from flask import Response

from cadenzaanalytics.response.extension_response import ExtensionResponse


class ErrorResponse(ExtensionResponse):
    def __init__(self, message: str, status: int = 400):
        self._message = message
        self._status = status

    def get_response(self):
        return self._create_response(self._message)

    def _get_response_json(self, message: str):
        error_message = {
            "message": message
        }

        return json.dumps(error_message)

    def _create_response(self, message: str):
        return Response(response=self._get_response_json(message), status=self._status, mimetype="application/json")
