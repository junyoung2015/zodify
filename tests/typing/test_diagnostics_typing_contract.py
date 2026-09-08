# pyright: strict
"""Static consumer contract for canonical diagnostics (Python 3.10 compatible)."""

from zodify import ValidationError, ValidationIssue, validate


def consume(error: ValidationError) -> tuple[str | int, ...] | None:
    details: tuple[ValidationIssue, ...] | None = error.details
    if details is None:
        return None
    issue: ValidationIssue = details[0]
    code: str = issue.code
    path: str = issue.path
    message: str = issue.message
    expected: str = issue.expected
    got: str = issue.got
    assert code and message and expected and got and path
    return issue.loc


def immutable_fields(issue: ValidationIssue) -> None:
    issue.code = "other"  # type: ignore[misc] # pyright: ignore[reportAttributeAccessIssue]


def validate_payload() -> tuple[str | int, ...] | None:
    try:
        validate({"age": int}, {"age": "bad"}, error_mode="structured")
    except ValidationError as error:
        return consume(error)
    return None
