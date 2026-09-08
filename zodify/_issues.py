"""Canonical failure records and private legacy-compatible issue collection."""

from typing import NamedTuple, cast


class ValidationIssue(NamedTuple):
    """Immutable diagnostic. Messages omit values; locations may contain secrets.

    ``loc`` is authoritative; ``path`` retains the legacy human projection.
    Codes may grow additively. Human messages are not machine identifiers.
    """

    code: str
    loc: tuple[str | int, ...]
    path: str
    message: str
    expected: str
    got: str


_Location = tuple[str | int, ...] | None
_LegacyIssue = tuple[str, str, str, str]
_MESSAGES = {
    "missing_key": "Missing required key.",
    "unknown_key": "Unknown key.",
    "custom_validation_failed": "Custom validation failed.",
    "depth_exceeded": "Maximum dictionary depth exceeded.",
}


class _IssueList(list[_LegacyIssue]):
    def __init__(self) -> None:
        super().__init__()
        self.details: list[ValidationIssue] | None = []


def _child_loc(loc: _Location, key: object) -> _Location:
    # Do not stringify unsupported keys: that can run arbitrary user code.
    return loc + (cast(str | int, key),) if loc is not None and type(key) in (str, int) else None


def _record_issue(errors: list[_LegacyIssue], loc: _Location,
                  code: str, issue: _LegacyIssue) -> None:
    errors.append(issue)
    if isinstance(errors, _IssueList) and errors.details is not None:
        if loc is None:
            errors.details = None  # No lossless public location for this key.
            return
        path, _, expected, got = issue
        message = _MESSAGES.get(code, f"Expected {expected}; received {got}.")
        if code == "coercion_failed": message = f"Cannot coerce {got} to {expected}."
        errors.details.append(ValidationIssue(code, loc, path, message, expected, got))
