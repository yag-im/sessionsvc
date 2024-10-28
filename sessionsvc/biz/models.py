from sqlalchemy import (
    TIMESTAMP,
    BigInteger,
    Column,
    FetchedValue,
    String,
)
from sqlalchemy.dialects.postgresql import JSONB

from sessionsvc.biz.sqldb import sqldb


class SessionDAO(sqldb.Model):
    __tablename__ = "sessions"
    __table_args__ = {"schema": "sessions"}
    id = Column(String, primary_key=True)
    app_release_uuid = Column(String, nullable=False)
    container = Column(JSONB)
    status = Column(String, nullable=False)
    updated = Column(TIMESTAMP, server_default=FetchedValue())
    user_id = Column(BigInteger, nullable=False)
    ws_conn = Column(JSONB, nullable=False)


class SessionsLogDAO(sqldb.Model):
    __tablename__ = "sessions_logs"
    __table_args__ = {"schema": "sessions"}
    id = Column(BigInteger, primary_key=True)
    app_release_uuid = Column(String, nullable=False)
    container = Column(JSONB)
    session_id = Column(String, nullable=False)  # sessions.id
    status = Column(String, nullable=False)
    user_id = Column(BigInteger, nullable=False)
    ws_conn = Column(JSONB, nullable=False)


class WebRTCStatsLogsDAO(sqldb.Model):
    __tablename__ = "webrtc_stats_logs"
    __table_args__ = {"schema": "stats"}
    id = Column(BigInteger, primary_key=True)
    app_release_uuid = Column(String, nullable=False)
    region = Column(String, nullable=False)
    session_id = Column(String, nullable=False)  # sessions.id
    stats = Column(JSONB)
    user_id = Column(BigInteger)


class UsersDcsDAO(sqldb.Model):
    __tablename__ = "users_dcs"
    __table_args__ = {"schema": "stats"}
    id = Column(BigInteger, primary_key=True)
    dcs = Column(JSONB)
    user_id = Column(BigInteger)
