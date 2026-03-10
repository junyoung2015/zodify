"""Head-to-head validation benchmark: zodify vs competitors.

Competitor libraries are optional for local benchmarking. If a dependency is
missing, that competitor is skipped with an install hint.
"""

import statistics
import time
from collections.abc import Callable

ROUNDS = 10000
WARMUP = 500

data = {"name": "Alice", "age": 30, "email": "alice@example.com"}
results: list[tuple[str, float]] = []


def _run_benchmark(fn: Callable[[], object]) -> float:
    for _ in range(WARMUP):
        fn()
    times: list[float] = []
    for _ in range(ROUNDS):
        start = time.perf_counter()
        fn()
        end = time.perf_counter()
        times.append((end - start) * 1_000_000)
    return statistics.median(times)


def _record(name: str, fn: Callable[[], object]) -> None:
    median_us = _run_benchmark(fn)
    results.append((name, median_us))
    print(f"{name}: {median_us:.2f} us/op  ({1_000_000/median_us:.0f} ops/sec)")


def _skip(name: str, package_name: str) -> None:
    print(f"{name}: skipped (missing optional dependency '{package_name}')")


# --- zodify (always expected) ---
from zodify import validate

schema_z = {"name": str, "age": int, "email": str}
_record("zodify", lambda: validate(schema_z, data))

# --- pydantic ---
try:
    from pydantic import BaseModel, Field
except ModuleNotFoundError:
    _skip("pydantic", "pydantic")
else:
    class UserModel(BaseModel):
        name: str = Field(min_length=1, max_length=50)
        age: int = Field(ge=0, le=150)
        email: str

    _record("pydantic", lambda: UserModel(**data))

# --- cerberus ---
try:
    from cerberus import Validator as CerberusValidator
except ModuleNotFoundError:
    _skip("cerberus", "cerberus")
else:
    cerb_schema = {
        "name": {"type": "string", "minlength": 1, "maxlength": 50},
        "age": {"type": "integer", "min": 0, "max": 150},
        "email": {"type": "string"},
    }
    cerberus_validator = CerberusValidator(cerb_schema)
    _record("cerberus", lambda: cerberus_validator.validate(data))

# --- voluptuous ---
try:
    from voluptuous import All, Length, Range, Required, Schema
except ModuleNotFoundError:
    _skip("voluptuous", "voluptuous")
else:
    vol_schema = Schema(
        {
            Required("name"): All(str, Length(min=1, max=50)),
            Required("age"): All(int, Range(min=0, max=150)),
            Required("email"): str,
        }
    )
    _record("voluptuous", lambda: vol_schema(data))

# --- schema ---
try:
    from schema import And, Schema as SSchema
except ModuleNotFoundError:
    _skip("schema", "schema")
else:
    s_schema = SSchema(
        {
            "name": And(str, lambda s: 1 <= len(s) <= 50),
            "age": And(int, lambda n: 0 <= n <= 150),
            "email": str,
        }
    )
    _record("schema", lambda: s_schema.validate(data))

print("\n--- SUMMARY (sorted by speed) ---")
results.sort(key=lambda item: item[1])
fastest = results[0][1]
for name, us in results:
    ratio = us / fastest
    tag = " (fastest)" if ratio == 1.0 else ""
    print(f"  {name:15s}  {us:8.2f} us/op  {1_000_000/us:>10,.0f} ops/sec  {ratio:.1f}x{tag}")
