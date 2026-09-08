"""Exact JSON Schema export for plain dict and Schema declarations."""

import json

from zodify import Optional, Schema, to_json_schema


class ServiceConfig(Schema):
    host: str
    debug: bool | None


def main() -> None:
    plain = to_json_schema({"service": {"host": str, "label": Optional(str)}})
    declared = to_json_schema(ServiceConfig)
    print("=== Plain dict export ===")
    print(json.dumps(plain, indent=2, sort_keys=True))
    print()
    print("=== Schema class export ===")
    print(json.dumps(declared, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

# Expected output:
# === Plain dict export ===
# {
#   "$schema": "https://json-schema.org/draft/2020-12/schema",
#   "additionalProperties": false,
#   "properties": {
#     "service": {
#       "additionalProperties": false,
#       "properties": {
#         "host": {
#           "type": "string"
#         },
#         "label": {
#           "type": "string"
#         }
#       },
#       "required": [
#         "host"
#       ],
#       "type": "object"
#     }
#   },
#   "required": [
#     "service"
#   ],
#   "type": "object"
# }
#
# === Schema class export ===
# {
#   "$schema": "https://json-schema.org/draft/2020-12/schema",
#   "additionalProperties": false,
#   "properties": {
#     "debug": {
#       "anyOf": [
#         {
#           "type": "boolean"
#         },
#         {
#           "type": "null"
#         }
#       ]
#     },
#     "host": {
#       "type": "string"
#     }
#   },
#   "required": [
#     "host",
#     "debug"
#   ],
#   "type": "object"
# }
