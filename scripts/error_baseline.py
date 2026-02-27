"""Capture all validation error strings for before/after diffing.

Usage:
    python scripts/error_baseline.py > baseline_before.txt
    # ... refactor ...
    python scripts/error_baseline.py > baseline_after.txt
    diff baseline_before.txt baseline_after.txt
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from zodify import validate, env, Optional

errors_collected = []


def capture(label, fn):
    """Run fn, capture ValueError/TypeError message."""
    try:
        fn()
        errors_collected.append(f"[{label}] NO ERROR")
    except (ValueError, TypeError) as e:
        errors_collected.append(f"[{label}] {e}")


# --- Type mismatches (primitive) ---
capture("int_got_str", lambda: validate({"a": int}, {"a": "x"}))
capture("str_got_int", lambda: validate({"a": str}, {"a": 42}))
capture("bool_got_int", lambda: validate({"a": bool}, {"a": 1}))
capture("float_got_str", lambda: validate({"a": float}, {"a": "x"}))
capture("int_got_bool", lambda: validate({"count": int}, {"count": True}))
capture("int_got_none", lambda: validate({"a": int}, {"a": None}))
capture("str_got_none", lambda: validate({"a": str}, {"a": None}))

# --- Missing required keys ---
capture("missing_single", lambda: validate({"a": int}, {}))
capture("missing_nested", lambda: validate({"db": {"host": str}}, {"db": {}}))
capture("missing_multiple", lambda: validate({"a": int, "b": str}, {}))

# --- Unknown key errors ---
capture("unknown_key", lambda: validate({"a": int}, {"a": 1, "extra": 2}))

# --- Nested dict errors ---
capture("nested_not_dict", lambda: validate({"db": {"host": str}}, {"db": "notadict"}))
capture("nested_type_mismatch", lambda: validate({"db": {"port": int}}, {"db": {"port": "bad"}}))
capture("nested_deep_3", lambda: validate({"a": {"b": {"c": int}}}, {"a": {"b": {"c": "x"}}}))
capture("nested_none", lambda: validate({"db": {"host": str}}, {"db": None}))

# --- List errors ---
capture("list_not_list", lambda: validate({"tags": [str]}, {"tags": "notalist"}))
capture("list_elem_mismatch", lambda: validate({"tags": [str]}, {"tags": ["a", 42]}))
capture("list_none", lambda: validate({"tags": [str]}, {"tags": None}))
capture("list_of_dicts_err", lambda: validate({"users": [{"name": str}]}, {"users": [{"name": 42}]}))
capture("list_of_lists_err", lambda: validate({"m": [[int]]}, {"m": [[1, "bad"]]}))

# --- Coercion failures ---
capture("coerce_int_fail", lambda: validate({"x": int}, {"x": "abc"}, coerce=True))
capture("coerce_float_fail", lambda: validate({"x": float}, {"x": "abc"}, coerce=True))
capture("coerce_bool_fail", lambda: validate({"x": bool}, {"x": "maybe"}, coerce=True))
capture("coerce_empty_int", lambda: validate({"x": int}, {"x": ""}, coerce=True))
capture("coerce_empty_float", lambda: validate({"x": float}, {"x": ""}, coerce=True))
capture("coerce_empty_bool", lambda: validate({"x": bool}, {"x": ""}, coerce=True))
capture("coerce_bool_non_str", lambda: validate({"x": int}, {"x": True}, coerce=True))

# --- Coercion in lists ---
capture("list_coerce_fail", lambda: validate({"n": [float]}, {"n": ["bad"]}, coerce=True))

# --- Multi-error aggregation ---
capture("multi_errors", lambda: validate(
    {"name": str, "db": {"port": int}, "tags": [str]},
    {"db": {"port": "bad"}, "tags": ["ok", 42]},
))

# --- Optional with wrong type ---
capture("optional_wrong_type", lambda: validate({"port": Optional(int)}, {"port": "abc"}))
capture("optional_coerce_fail", lambda: validate({"port": Optional(int)}, {"port": "abc"}, coerce=True))

# --- Custom validation failure ---
capture("callable_fail", lambda: validate({"port": lambda v: 1 <= v <= 65535}, {"port": 99999}))

# --- Set/tuple type mismatch ---
capture("set_mismatch", lambda: validate({"tags": set}, {"tags": [1, 2]}))

# Print all collected errors deterministically
for line in errors_collected:
    print(line)
