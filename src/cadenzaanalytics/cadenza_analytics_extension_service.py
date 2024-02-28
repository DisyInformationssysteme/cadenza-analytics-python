"""Configures and starts the service that runs a http server to allow disy Cadenza to detect individual extensions
and execute their analytics function."""
import json

from flask import Flask, Response
from flask_cors import CORS

from cadenzaanalytics.cadenza_analytics_extension import CadenzaAnalyticsExtension


class CadenzaAnalyticsExtensionService:
    def __init__(self):
        self._analytics_extensions = []

        self._app = Flask('cadenzaanalytics')
        CORS(self._app)

        self._app.add_url_rule("/", view_func=self._list_extensions)

    def add_analytics_extension(self, analytics_extension: CadenzaAnalyticsExtension):
        self._analytics_extensions.append(analytics_extension)

        self._app.add_url_rule("/" + analytics_extension.relative_path,
                               view_func=analytics_extension.get_capabilities,
                               endpoint=analytics_extension.relative_path + "_get",
                               methods=['GET'])
        self._app.add_url_rule("/" + analytics_extension.relative_path,
                               view_func=analytics_extension.handle_request,
                               endpoint=analytics_extension.relative_path + "_post",
                               methods=['POST'])

    def run_development_server(self, port: int = 5000):
        self._app.run(port=port)

    def __call__(self, *args, **kwargs):
        return self._app

    def _list_extensions(self):
        result_dict = {'extensions': []}

        for extension in self._analytics_extensions:
            result_dict['extensions'].append({'relativePath': extension.relative_path,
                                              'extensionPrintName': extension.print_name,
                                              'extensionType': extension.extension_type})

        return Response(response=json.dumps(result_dict, default=str), status=200, mimetype="application/json")
