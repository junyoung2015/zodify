from zodify import Optional, validate

schema = {"host": str, "port": int, "debug": Optional(bool, False)}
config = {"host": "localhost", "port": 8080}
assert validate(schema, config)["debug"] is False
with_typo = dict(config, debgu=True)
try:
    validate(schema, with_typo)
except ValueError:
    pass  # Reject unknown keys: catch misspelled configuration.
else:
    raise AssertionError("Expected unknown-key failure")
clean = validate(schema, with_typo, unknown_keys="strip")
assert "debgu" not in clean  # Explicitly drops data; does not repair the typo.
assert "debgu" in with_typo  # Original input is unchanged here.
print("config-validation: passed")
