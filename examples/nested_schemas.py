"""Nested schema composition with Optional keys and a nested union."""

from zodify import Optional, validate


def main() -> None:
    print("=== Success: nested composition ===")
    db_schema = {
        "host": str,
        "port": int,
    }
    service_schema = {
        "name": str,
        "mode": str | int,
    }
    config_schema = {
        "db": db_schema,
        "service": service_schema,
        "debug": Optional(bool, False),
        "region": Optional(str),
    }

    config_data = {
        "db": {"host": "localhost", "port": "5432"},
        "service": {"name": "api", "mode": 1},
    }
    print(validate(config_schema, config_data, coerce=True))
    print()

    print("=== Error: nested missing key ===")
    try:
        validate(
            config_schema,
            {"db": {"host": "localhost"}, "service": {"name": "api", "mode": 1}},
        )
    except ValueError as error:
        print(error)
    print()


if __name__ == "__main__":
    main()

# Expected output:
# === Success: nested composition ===
# {'db': {'host': 'localhost', 'port': 5432}, 'service': {'name': 'api', 'mode': 1}, 'debug': False}
# 
# === Error: nested missing key ===
# db.port: missing required key
