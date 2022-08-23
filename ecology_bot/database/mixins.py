import datetime

from sqlalchemy import Column, BigInteger, DateTime, func


class PkMixin:
    id = Column(BigInteger, primary_key=True, index=True)


class TimestampMixin:
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        server_onupdate=func.now(),
        onupdate=datetime.datetime.now,
    )
