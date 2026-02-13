"""Provides a service which encapsulates the configuration and execution of individual analytics extensions.
Runs an HTTP server which executes the individual extension's analytics function and serves an extension
discovery endpoint."""
import inspect
import json
from typing import Optional

from flask import Flask, Response
from flask_cors import CORS

from cadenzaanalytics.cadenza_analytics_extension import CadenzaAnalyticsExtension
from cadenzaanalytics.version import __version__


class CadenzaAnalyticsExtensionService:
    """A Flask-based service that runs and manages Cadenza analytics extensions.

    Provides HTTP endpoints for extension discovery and request handling.
    Register extensions using `add_analytics_extension()` and start the server
    with `run_development_server()` or access the Flask app via the `app` property.
    """

    def __init__(self) -> None:
        """Initialize the CadenzaAnalyticsExtensionService.

        Creates a Flask application with CORS support and sets up the
        extension discovery endpoint at the root path.
        """
        self._analytics_extensions = []

        self._app = Flask('cadenzaanalytics')
        CORS(self._app)

        self.logger = self._app.logger
        self.logger.info('Initializing cadenzaanalytics version "%s"...', __version__)

        self._app.add_url_rule("/", view_func=self._list_extensions)

    def add_analytics_extension(self, analytics_extension: CadenzaAnalyticsExtension) -> None:
        """Add an analytics extension to the service.

        Parameters
        ----------
        analytics_extension : CadenzaAnalyticsExtension
            The analytics extension to be added.

        Raises
        ------
        ValueError
            If the relative path is already in use or the analytics function has an invalid signature.
        """
        self.logger.info('Registering extension "%s" on relative path "%s"...',
                analytics_extension.print_name,
                analytics_extension.relative_path
            )

        # perform some validation checks
        if analytics_extension.relative_path in [x.relative_path for x in self._analytics_extensions]:
            msg = f'Relative path "{analytics_extension.relative_path}" is already in use by another extension.'
            self.logger.critical(msg)
            raise ValueError(msg)

        self._validate_analytics_function(analytics_extension._analytics_function)  # pylint: disable=W0212

        self._analytics_extensions.append(analytics_extension)

        self._app.add_url_rule("/" + analytics_extension.relative_path,
                               view_func=analytics_extension.get_capabilities,
                               endpoint=analytics_extension.relative_path + "_get",
                               methods=['GET'])
        self._app.add_url_rule("/" + analytics_extension.relative_path,
                               view_func=analytics_extension.handle_request,
                               endpoint=analytics_extension.relative_path + "_post",
                               methods=['POST'])

    def run_development_server(self, port: int = 5000, debug: Optional[bool] = None) -> None:
        """Start a development server which runs the service.

        Parameters
        ----------
        port : int, optional
            The port where the service is exposed, by default 5000.
        debug : Optional[bool], optional
            If True, the server will automatically reload for code changes
            and show a debugger in case an exception happened.
        """
        self._app.run(port=port, debug=debug)

    @property
    def app(self) -> Flask:
        """Get the underlying Flask application instance.

        Returns
        -------
        Flask
            The Flask application managing the analytics extensions.
        """
        return self._app

    def _validate_analytics_function(self, func) -> None:
        """Validate that analytics function has correct signature.

        Parameters
        ----------
        func : Callable
            The analytics function to validate.

        Raises
        ------
        ValueError
            If the function does not accept exactly 1 positional argument.
        """
        try:
            sig = inspect.signature(func)
            params = [p for p in sig.parameters.values()
                      if p.kind in (inspect.Parameter.POSITIONAL_ONLY,
                                    inspect.Parameter.POSITIONAL_OR_KEYWORD)]
            if len(params) != 1:
                raise ValueError(f"Function must accept exactly 1 positional argument, got {len(params)}")
        except (ValueError, TypeError) as err:
            self.logger.critical("Invalid analytics function: %s", err)
            raise ValueError(str(err)) from err

    def _list_extensions(self) -> Response:
        """List all registered analytics extensions.

        Returns
        -------
        Response
            JSON response containing list of extensions with their metadata.
        """
        result_dict = {'extensions': []}

        for extension in self._analytics_extensions:
            result_dict['extensions'].append({'relativePath': extension.relative_path,
                                              'extensionPrintName': extension.print_name,
                                              'extensionType': extension.extension_type})
        result_dict['cadenzaAnalyticsVersion'] = __version__
        return Response(response=json.dumps(result_dict, default=str), status=200, mimetype="application/json")
