"""Unit tests for logging configuration."""
import json
import logging

import pytest
from cadenzaanalytics.logging_config import configure_logging


class TestLoggingConfig:
    """Test suite for configure_logging."""

    def teardown_method(self):
        """Reset logger state so tests don't leak configuration into one another."""
        for name in (None, 'gunicorn.error', 'gunicorn.access'):
            logger = logging.getLogger(name)
            logger.handlers = []
            logger.propagate = True

    def test_invalid_log_format_raises(self, monkeypatch):
        """An unsupported CADENZAANALYTICS_LOG_FORMAT value should raise a ValueError."""
        monkeypatch.setenv('CADENZAANALYTICS_LOG_FORMAT', 'bogus')
        with pytest.raises(ValueError, match='CADENZAANALYTICS_LOG_FORMAT'):
            configure_logging()

    def test_ecs_format_produces_ecs_json(self, monkeypatch, capsys):
        """The 'ecs' format should produce ECS-conformant JSON, stamped with the service name/version."""
        monkeypatch.setenv('CADENZAANALYTICS_LOG_FORMAT', 'ecs')
        configure_logging()

        logging.getLogger('some.dependency').warning('dependency warning')

        record = json.loads(capsys.readouterr().err.strip())
        assert record['message'] == 'dependency warning'
        # per the ECS logging spec, '@timestamp', 'log.level' and 'message' stay flat/dotted top-level keys
        assert record['log.level'] == 'warning'
        assert record['log']['logger'] == 'some.dependency'
        assert record['service']['name'] == 'cadenzaanalytics'

    def test_plain_format_is_not_json(self, monkeypatch, capsys):
        """The default 'plain' format should produce a human-readable line, not JSON."""
        monkeypatch.delenv('CADENZAANALYTICS_LOG_FORMAT', raising=False)
        configure_logging()

        logging.getLogger('some.dependency').warning('dependency warning')

        line = capsys.readouterr().err.strip()
        assert 'dependency warning' in line
        with pytest.raises(json.JSONDecodeError):
            json.loads(line)

    def test_log_level_is_case_insensitive(self, monkeypatch):
        """CADENZAANALYTICS_LOG_LVL should be accepted regardless of case, since logging.setLevel()
        only recognizes uppercase level names and would otherwise raise a ValueError."""
        monkeypatch.setenv('CADENZAANALYTICS_LOG_LVL', 'debug')
        configure_logging()

        assert logging.getLogger().getEffectiveLevel() == logging.DEBUG

    def test_gunicorn_loggers_are_repointed_at_our_handler(self, monkeypatch, capsys):
        """gunicorn attaches its own handlers to 'gunicorn.error'/'gunicorn.access' with propagate=False
        before the app is imported; configure_logging() must re-point them at our own handler so gunicorn's
        own log lines come out in the configured format too, without any gunicorn-side configuration."""
        gunicorn_access = logging.getLogger('gunicorn.access')
        gunicorn_access.propagate = False
        gunicorn_access.addHandler(logging.StreamHandler())

        monkeypatch.setenv('CADENZAANALYTICS_LOG_FORMAT', 'ecs')
        configure_logging()

        gunicorn_access.info('127.0.0.1 - - "GET / HTTP/1.1" 200 -')

        record = json.loads(capsys.readouterr().err.strip())
        assert record['log']['logger'] == 'gunicorn.access'
        assert record['service']['name'] == 'cadenzaanalytics'
