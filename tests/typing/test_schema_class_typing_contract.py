"""Typing smoke for the live Schema public API."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from zodify import Schema, Validator, validate


if TYPE_CHECKING:
    class Credentials(Schema):
        username: str
        password: str


    class DatabaseConfig(Schema):
        host: str
        port: int
        creds: Credentials
        helper_constant: ClassVar[str] = "ignore-me"


    validated = validate(
        DatabaseConfig,
        {
            "host": "db.local",
            "port": 5432,
            "creds": {"username": "kai", "password": "pw"},
        },
    )
    host_name: str = validated.host
    port_number: int = validated.port
    nested_username: str = validated.creds.username

    validator = Validator()
    validated_via_instance = validator.validate(
        DatabaseConfig,
        {
            "host": "db.internal",
            "port": 15432,
            "creds": {"username": "kai", "password": "pw"},
        },
    )
    instance_host_name: str = validated_via_instance.host

    plain = validate({"host": str}, {"host": "db.local"})
    plain_host: str = plain["host"]
