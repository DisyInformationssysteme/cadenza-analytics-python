"""Provides a service which encapsulates the configuration and execution of individual analytics extensions. Runs a http server which
executes the individual extensions analytics function and serves an extension discovery endpoint."""
import json

from flask import Flask, Response
from flask_cors import CORS

from cadenzaanalytics.cadenza_analytics_extension import CadenzaAnalyticsExtension


class CadenzaAnalyticsExtensionService:
    """A service that runs and manages Cadenza analytics extensions.
    """
    def __init__(self):
        self._analytics_extensions = []

        self._app = Flask('cadenzaanalytics')
        CORS(self._app)

        self._app.add_url_rule("/", view_func=self._list_extensions)

    def add_analytics_extension(self, analytics_extension: CadenzaAnalyticsExtension):
        """Add an analytics extension to the service.

        Parameters:
        ----------
        analytics_extension : CadenzaAnalyticsExtension
            The analytics extension to be added.
        """        
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
        """Start a development server wich runs the service.

        Parameters:
        ----------
        port : int, optional
            The port where the service is exposed, default 5000.
        """        
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
