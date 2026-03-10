"""Typing smoke for the live Schema public API."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Optional, Union

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
        replicas: list[Credentials]
        mode: Union[str, int]
        timeout: Optional[int]


    validated: DatabaseConfig = validate(
        DatabaseConfig,
        {
            "host": "db.local",
            "port": 5432,
            "creds": {"username": "kai", "password": "pw"},
            "replicas": [{"username": "kai", "password": "pw"}],
            "mode": "read-only",
            "timeout": None,
        },
    )
    host_name: str = validated.host
    port_number: int = validated.port
    nested_username: str = validated.creds.username
    replica_username: str = validated.replicas[0].username
    stripped: DatabaseConfig = validate(
        DatabaseConfig,
        {
            "host": "db.local",
            "port": 5432,
            "creds": {"username": "kai", "password": "pw"},
            "replicas": [{"username": "kai", "password": "pw"}],
            "mode": "read-only",
            "timeout": None,
            "extra": "drop-me",
        },
        unknown_keys="strip",
    )
    stripped_host_name: str = stripped.host

    validator = Validator()
    validated_via_instance: DatabaseConfig = validator.validate(
        DatabaseConfig,
        {
            "host": "db.internal",
            "port": 15432,
            "creds": {"username": "kai", "password": "pw"},
            "replicas": [{"username": "kai", "password": "pw"}],
            "mode": 1,
            "timeout": 30,
        },
    )
    instance_host_name: str = validated_via_instance.host
    stripped_via_instance: DatabaseConfig = validator.validate(
        DatabaseConfig,
        {
            "host": "db.internal",
            "port": 15432,
            "creds": {"username": "kai", "password": "pw"},
            "replicas": [{"username": "kai", "password": "pw"}],
            "mode": 1,
            "timeout": 30,
            "extra": "drop-me",
        },
        unknown_keys="strip",
    )
    stripped_instance_host_name: str = stripped_via_instance.host

    plain = validate({"host": str}, {"host": "db.local"})
    plain_host: str = plain["host"]
    stripped_plain = validator.validate(
        {"host": str},
        {"host": "db.local", "extra": "drop-me"},
        unknown_keys="strip",
    )
    stripped_plain_host: str = stripped_plain["host"]
