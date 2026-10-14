import datetime
import typing as t

from sqlalchemy import (
    TIMESTAMP,
    BigInteger,
    FetchedValue,
    String,
)
from sqlalchemy.dialects.postgresql import (
    ENUM,
    JSONB,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from sessionsvc.biz.sqldb import sqldb

# existing db type; values must match dto.SessionStatus
SessionStatusType = ENUM(
    "pending",
    "active",
    "paused",
    "closed",
    name="session_status",
    schema="sessions",
    create_type=False,
)


class SessionDAO(sqldb.Model):
    __tablename__ = "sessions"
    __table_args__ = {"schema": "sessions"}
    id: Mapped[str] = mapped_column(String, primary_key=True)
    app_release_uuid: Mapped[str] = mapped_column(String, nullable=False)
    container: Mapped[dict[str, t.Any] | None] = mapped_column(JSONB)
    status: Mapped[str] = mapped_column(SessionStatusType, nullable=False)
    # nullable in the schema, but server-populated and treated as always set (see SessionDC.updated)
    updated: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, nullable=True, server_default=FetchedValue())
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    ws_conn: Mapped[dict[str, t.Any]] = mapped_column(JSONB, nullable=False)


class SessionsLogDAO(sqldb.Model):
    __tablename__ = "sessions_logs"
    __table_args__ = {"schema": "sessions"}
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    app_release_uuid: Mapped[str] = mapped_column(String, nullable=False)
    container: Mapped[dict[str, t.Any] | None] = mapped_column(JSONB)
    session_id: Mapped[str] = mapped_column(String, nullable=False)  # sessions.id
    status: Mapped[str] = mapped_column(SessionStatusType, nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    ws_conn: Mapped[dict[str, t.Any]] = mapped_column(JSONB, nullable=False)


class WebRTCStatsLogsDAO(sqldb.Model):
    __tablename__ = "webrtc_stats_logs"
    __table_args__ = {"schema": "stats"}
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    app_release_uuid: Mapped[str] = mapped_column(String, nullable=False)
    region: Mapped[str] = mapped_column(String, nullable=False)
    session_id: Mapped[str] = mapped_column(String, nullable=False)  # sessions.id
    stats: Mapped[dict[str, t.Any] | None] = mapped_column(JSONB)
    user_id: Mapped[int | None] = mapped_column(BigInteger)


class UsersDcsDAO(sqldb.Model):
    __tablename__ = "users_dcs"
    __table_args__ = {"schema": "stats"}
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    # region -> recent rtts
    dcs: Mapped[dict[str, list[float]] | None] = mapped_column(JSONB)
    user_id: Mapped[int | None] = mapped_column(BigInteger)
