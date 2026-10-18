import sys
from importlib.metadata import version
from zodify import Schema, validate

release = version("zodify")
assert release in {"0.8.0", "0.8.1"}

class Port(Schema):
    port: int

def outcome(data):
    try:
        return dict(validate(Port, data))
    except ValueError as error:
        return str(error)

missing = outcome({})
valid = outcome({"port": 8080})
old_deferred = release == "0.8.0" and sys.version_info >= (3, 14)
assert missing == ({} if old_deferred else "port: missing required key")
assert valid == ("port: unknown key" if old_deferred else {"port": 8080})
print("Missing-field and valid-input checks match the published version")
