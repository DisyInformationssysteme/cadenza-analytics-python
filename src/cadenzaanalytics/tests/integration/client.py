"""A small client speaking the multipart protocol without library serializers."""

import csv
from email import policy
from email.parser import BytesParser
from io import BytesIO, StringIO
import json

import cadenzaanalytics as ca


class ExtensionReply:
    """Read a response as an independent Cadenza-compatible client would."""

    def __init__(self, response):
        self.status_code = response.status_code
        self.content_type = response.content_type
        self.json = response.get_json(silent=True)
        self.parts = {}
        if response.mimetype == "multipart/form-data":
            message = BytesParser(policy=policy.default).parsebytes(
                f"Content-Type: {response.content_type}\r\nMIME-Version: 1.0\r\n\r\n".encode()
                + response.data
            )
            assert message.is_multipart(), "Response must contain valid multipart data"
            for part in message.iter_parts():
                name = part.get_param("name", header="Content-Disposition")
                assert name not in self.parts, f"Duplicate response part: {name}"
                self.parts[name] = part.get_payload(decode=True)

    @property
    def metadata(self):
        return json.loads(self.parts["metadata"])

    @property
    def container(self):
        return self.metadata["dataContainers"][0]

    @property
    def content(self):
        return self.parts[self.container["name"]]

    @property
    def text(self):
        return self.content.decode("utf-8")

    @property
    def rows(self):
        """Read ordinary CSV values; use text assertions to distinguish null and empty."""
        return list(csv.reader(StringIO(self.text, newline=""), delimiter=";"))


class ExtensionClient:
    """Exercise the real service, routing, parsing, callback, and response encoding."""

    def __init__(self, extension):
        service = ca.CadenzaAnalyticsExtensionService()
        service.add_analytics_extension(extension)
        # Surface exceptions with useful tracebacks instead of an opaque HTTP 500.
        service.app.testing = True
        self.http = service.app.test_client()
        self.path = "/" + extension.relative_path

    def invoke(self, *, columns=None, parameters=None, csv_data=None, metadata=None,
               headers=None, part_style="files"):
        if metadata is None:
            metadata = {
                "dataContainers": [{"name": "data", "type": "text/csv", "columns": columns}] if columns else [],
                "parameters": parameters if parameters is not None else [],
            }
        parts = {"metadata": json.dumps(metadata)}
        if csv_data is not None:
            parts["data"] = csv_data
        if part_style == "files":
            parts = {
                name: (BytesIO(value.encode("utf-8")), name, "application/json" if name == "metadata" else "text/csv")
                for name, value in parts.items()
            }
        elif part_style != "fields":
            raise ValueError(f"Unknown multipart style: {part_style}")
        return ExtensionReply(self.http.post(
            self.path, data=parts, headers=headers, content_type="multipart/form-data",
        ))


def column(name, data_type="string", **metadata):
    """Describe a wire-format column; enum strings are deliberately literal."""
    return {"name": name, "printName": name, "dataType": data_type, "attributeGroupName": "values", **metadata}


def parameter(name, data_type, value, **metadata):
    return {"name": name, "printName": name, "dataType": data_type, "value": value, **metadata}
