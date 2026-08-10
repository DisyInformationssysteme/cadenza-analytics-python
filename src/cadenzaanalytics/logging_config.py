"""Configures logging for the `cadenzaanalytics` package.

The configured handler is attached to the root logger, and `disable_existing_loggers` is left `False`, so this
also governs log output from dependent packages (e.g. Flask, Werkzeug) and from analytics extensions built with
`cadenzaanalytics`, as long as their loggers propagate to root, which is the default in standard Python logging.
"""
import os
from logging.config import dictConfig
from typing import Any, Dict

import ecs_logging

from cadenzaanalytics.version import __version__

_PLAIN_FORMATTER_CONFIG = {
    'format': '[%(asctime)s] [%(process)d] [%(levelname)s] [%(module)s] %(message)s',
    'datefmt': '%Y-%m-%d %H:%M:%S %z'
}


class CadenzaEcsFormatter(ecs_logging.StdlibFormatter):
    """An `ecs_logging.StdlibFormatter` that additionally stamps every record with `service.name`
    and `service.version`, identifying the `cadenzaanalytics` version that produced the log line."""

    def format_to_ecs(self, record) -> Dict[str, Any]:
        result = super().format_to_ecs(record)
        result.setdefault('service', {})['name'] = 'cadenzaanalytics'
        result['service']['version'] = __version__
        return result


def configure_logging() -> None:
    """Configure the root logger from the `CADENZAANALYTICS_LOG_LVL` and `CADENZAANALYTICS_LOG_FORMAT`
    environment variables.

    `CADENZAANALYTICS_LOG_LVL` sets the root log level (default `INFO`).
    `CADENZAANALYTICS_LOG_FORMAT` selects the output format: `plain` (default) for a human-readable,
    gunicorn-like line format, or `ecs` for Elastic Common Schema (ECS) conformant JSON, suited for
    log aggregation in container deployments.

    Raises
    ------
    ValueError
        If `CADENZAANALYTICS_LOG_FORMAT` is set to a value other than `plain` or `ecs`.
    """
    log_format = os.environ.get('CADENZAANALYTICS_LOG_FORMAT', 'plain').lower()

    if log_format == 'plain':
        formatter_config = _PLAIN_FORMATTER_CONFIG
    elif log_format == 'ecs':
        formatter_config = {'()': CadenzaEcsFormatter}
    else:
        raise ValueError(
            f'Invalid CADENZAANALYTICS_LOG_FORMAT "{log_format}". Supported values are "plain" and "ecs".'
        )

    log_level = os.environ.get('CADENZAANALYTICS_LOG_LVL', 'INFO').upper()

    dictConfig({
        'disable_existing_loggers': False,
        'version': 1,
        'formatters': {'default': formatter_config},
        'handlers': {'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        }},
        'root': {
            'level': log_level,
            'handlers': ['wsgi']
        },
        # gunicorn configures 'gunicorn.error'/'gunicorn.access' with its own handlers and
        # propagate=False before this module is imported; re-pointing them at our own handler here
        # keeps gunicorn's own logs in the same format, without requiring any gunicorn-side configuration.
        'loggers': {
            'gunicorn.error': {'level': log_level, 'handlers': ['wsgi'], 'propagate': False},
            'gunicorn.access': {'level': log_level, 'handlers': ['wsgi'], 'propagate': False}
        }
    })
