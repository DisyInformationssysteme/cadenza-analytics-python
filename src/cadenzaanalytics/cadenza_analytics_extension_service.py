"""Provides a service which encapsulates the configuration and execution of individual analytics extensions.
Runs a http server which executes the individual extensions analytics function and serves an extension
discovery endpoint."""
import json
import errno
import sys

from flask import Flask, Response
from flask_cors import CORS

from cadenzaanalytics.cadenza_analytics_extension import CadenzaAnalyticsExtension
from cadenzaanalytics.version import __version__

class CadenzaAnalyticsExtensionService:
    """A service that runs and manages Cadenza analytics extensions.
    """
    def __init__(self):
        self._analytics_extensions = []

        self._app = Flask('cadenzaanalytics')
        CORS(self._app)

        self.logger = self._app.logger
        self.logger.info('Initializing cadenzaanalytics version "%s"...', __version__)

        self._app.add_url_rule("/", view_func=self._list_extensions)

    def add_analytics_extension(self, analytics_extension: CadenzaAnalyticsExtension):
        """Add an analytics extension to the service.

        Parameters:
        ----------
        analytics_extension : CadenzaAnalyticsExtension
            The analytics extension to be added.
        """

        self.logger.info('Registering extension "%s" on relative path "%s"...',
                analytics_extension.print_name,
                analytics_extension.relative_path
            )

        # perform some validation checks
        if analytics_extension.relative_path in [x.relative_path for x in self._analytics_extensions]:
            self.logger.critical('Relative path "%s" is already in use by another extension. Exiting...',
                    analytics_extension.relative_path)
            sys.exit(errno.EINTR)
        if analytics_extension._analytics_function.__code__.co_argcount != 1: # pylint: disable=W0212
            self.logger.critical('The analytics function "%s()" takes 1 positional arguments, but %s given. Exiting...',
                    analytics_extension._analytics_function.__name__,            # pylint: disable=W0212
                    analytics_extension._analytics_function.__code__.co_argcount # pylint: disable=W0212
                )
            sys.exit(errno.EINTR)

        self._analytics_extensions.append(analytics_extension)

        self._app.add_url_rule("/" + analytics_extension.relative_path,
                               view_func=analytics_extension.get_capabilities,
                               endpoint=analytics_extension.relative_path + "_get",
                               methods=['GET'])
        self._app.add_url_rule("/" + analytics_extension.relative_path,
                               view_func=analytics_extension.handle_request,
                               endpoint=analytics_extension.relative_path + "_post",
                               methods=['POST'])

    def run_development_server(self, port:int=5000, debug:bool=None):
        """Start a development server which runs the service.

        Parameters:
        ----------
        port : int, optional
            The port where the service is exposed, default 5000.
        debug : bool, optional
            If the debug flag is set the server will automatically reload for code changes
            and show a debugger in case an exception happened.
        """
        self._app.run(port=port, debug=debug)

    def __call__(self, *args, **kwargs):
        return self._app

    def _list_extensions(self):
        result_dict = {'extensions': []}

        for extension in self._analytics_extensions:
            result_dict['extensions'].append({'relativePath': extension.relative_path,
                                              'extensionPrintName': extension.print_name,
                                              'extensionType': extension.extension_type})

        return Response(response=json.dumps(result_dict, default=str), status=200, mimetype="application/json")
