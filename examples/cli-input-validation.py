import argparse
from zodify import validate

parser = argparse.ArgumentParser()
parser.add_argument("--port", required=True)
parser.add_argument("--debug", default="false")
schema = {"port": int, "debug": bool}
args = vars(parser.parse_args(["--port", "8080", "--debug", "yes"]))
assert validate(schema, args, coerce=True) == {"port": 8080, "debug": True}
try:
    validate(schema, {"port": "not-a-port", "debug": "false"}, coerce=True)
except ValueError:
    pass
else:
    raise AssertionError("Expected conversion failure")
print("cli-input-validation: passed")
