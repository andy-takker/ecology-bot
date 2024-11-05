from dataclasses import dataclass, field
from os import environ

from aiomisc_log import LogFormat, LogLevel


@dataclass(frozen=True, kw_only=True, slots=True)
class AppConfig:
    title: str = field(default_factory=lambda: environ.get("APP_TITLE", "Ecology Bot"))
    description: str = field(
        default_factory=lambda: environ.get(
            "APP_DESCRIPTION", "Web application for library"
        )
    )
    version: str = field(default_factory=lambda: environ.get("APP_VERSION", "1.0.0"))
    pool_size: int = field(
        default_factory=lambda: int(environ.get("APP_POOL_SIZE", 10))
    )
    debug: bool = field(
        default_factory=lambda: environ.get("APP_DEBUG", "False").lower() == "true"
    )


def get_log_level() -> LogLevel:
    log_level_str = environ.get("APP_LOG_LEVEL", LogLevel.default())
    if log_level_str not in LogLevel.choices():
        raise ValueError("APP_LOG_LEVEL is not valid")
    return LogLevel[log_level_str]


def get_log_format() -> LogFormat:
    log_format_str = environ.get("APP_LOG_FORMAT", LogFormat.default())
    if log_format_str not in LogFormat.choices():
        raise ValueError("APP_LOG_FORMAT is not valid")
    return LogFormat[log_format_str]


@dataclass(frozen=True, kw_only=True, slots=True)
class LogConfig:
    level: LogLevel = field(default_factory=get_log_level)
    format: LogFormat = field(default_factory=get_log_format)


@dataclass(frozen=True, kw_only=True, slots=True)
class SecretConfig:
    secret: str = field(default_factory=lambda: environ.get("APP_SECRET", "secret"))
