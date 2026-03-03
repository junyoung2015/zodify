"""Self-contained environment variable loading with env()."""

import os

from zodify import env


def main() -> None:
    print("=== Typed env loading ===")
    os.environ["EXAMPLE_PORT"] = "8080"
    os.environ["EXAMPLE_DEBUG"] = "yes"
    os.environ["EXAMPLE_HOST"] = "localhost"
    print(env("EXAMPLE_PORT", int))
    print(env("EXAMPLE_DEBUG", bool))
    print(env("EXAMPLE_HOST", str))
    print()

    print("=== Default value ===")
    os.environ.pop("EXAMPLE_TIMEOUT", None)
    print(env("EXAMPLE_TIMEOUT", int, 30))
    print()

    print("=== Error: missing required env var ===")
    os.environ.pop("EXAMPLE_REQUIRED_TOKEN", None)
    try:
        env("EXAMPLE_REQUIRED_TOKEN", str)
    except ValueError as error:
        print(error)
    print()


if __name__ == "__main__":
    main()

# Expected output:
# === Typed env loading ===
# 8080
# True
# localhost
# 
# === Default value ===
# 30
# 
# === Error: missing required env var ===
# EXAMPLE_REQUIRED_TOKEN: missing required env var
