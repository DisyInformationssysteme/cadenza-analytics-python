# Standalone extension scenarios

These tests run complete requests through a real `CadenzaAnalyticsExtensionService`:
multipart input → request objects and typed DataFrames → an analytics function →
multipart output readable by a client. They need no Cadenza installation, network,
server process, Docker container, credentials, or example extensions.

## Run

From the repository root, using Python 3.12 or another supported Python version:

```console
python -m venv .venv-tests
source .venv-tests/bin/activate
python -m pip install -e .
python -m pytest
```

The last command runs all tests, including the existing CSV and logging tests.
Once dependencies are installed, test execution is offline. Run just these
integration scenarios, or a single scenario, with:

```console
python -m pytest src/cadenzaanalytics/tests/integration -v
python -m pytest src/cadenzaanalytics/tests/integration/test_requests.py -k optional_column
```

## Scenarios

| File | Observable behavior |
| --- | --- |
| `test_discovery.py` | Discovery, capabilities, registration constraints |
| `test_configuration.py` | Invalid required configuration is rejected when defining an extension |
| `test_requests.py` | Typed tables, metadata lookups and groups, quoting, nulls, client context, compatibility |
| `test_parameters.py` | Every supported parameter type, geometry metadata, null versus absence, view dimensions |
| `test_responses.py` | A business calculation, data serialization, metadata strategies, visual output, error responses |
| `test_enrichment.py` | Automatic and explicit IDs, multiple keys, reordered results, invalid ID declarations |

The shared order fixture is ordinary JSON and CSV authored as a client payload.
Each test gets a fresh payload and a fresh service. Both multipart file uploads
and form fields are exercised. `client.py` contains the transport plumbing;
tests themselves use the public extension API and inspect client-visible results.
Response decoding uses Python's `email`, `json`, and `csv` modules, not production
serialization helpers. Exact CSV text is checked where quoting distinguishes an
empty string from a missing value. Other scenarios compare values and metadata.

Invalid requests and invalid extension results currently raise exceptions rather
than returning a structured validation response. The in-process client propagates
those exceptions so pytest reports useful tracebacks; rejection tests do not lock
in Flask's generic HTTP 500 page or exact exception wording.

## Geometry values

Request scenarios distinguish missing geometry values, invalid WKT text (including
an empty string), and valid empty geometries such as `POINT EMPTY`. Missing values
reach analytics without warnings; invalid text warns and becomes missing; valid
empty geometries remain geometries and survive a roundtrip.

## Coverage

Coverage tooling is optional and adds no dependency to the tests themselves:

```console
python -m pip install coverage
python -m coverage run -m pytest
python -m coverage report
python -m coverage html -d /tmp/cadenza-coverage
```

The project configuration measures production code, includes branches, and omits
test code. Use uncovered lines to find missing scenarios, rather than asserting
private attributes, cache structures, helper call counts, or framework internals.

To add a scenario, define a small analytics function, create it with the
`extension_client` fixture, invoke it with literal wire metadata and CSV, and
assert the values needed by the extension author or the receiving client. Keep
each new behavior independent of test order and external resources.
