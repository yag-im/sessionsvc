import datetime
import typing as t
from dataclasses import field
from enum import StrEnum

from marshmallow import Schema
from marshmallow_dataclass import dataclass

from sessionsvc.biz.models import SessionDAO
from sessionsvc.services.dto.appsvc import DcRegion


class SessionStatus(StrEnum):
    PENDING = "pending"
    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"


@dataclass
class SessionDC:
    @dataclass
    class WsConn:
        """Websocket connection parameters."""

        id: str  # unique ws connection id (used as a sticky session cookie value)
        consumer_id: str  # peer_id of the party awaiting for a stream (UA)
        producer_id: t.Optional[str] = None  # peer_id of the party producing a stream (streamd)
        Schema: t.ClassVar[t.Type[Schema]] = Schema  # pylint: disable=invalid-name

    @dataclass
    class Container:
        """Docker container parameters."""

        id: str
        node_id: str
        region: DcRegion
        Schema: t.ClassVar[t.Type[Schema]] = Schema  # pylint: disable=invalid-name

    app_release_uuid: str
    container: t.Optional[Container]
    updated: datetime.datetime
    user_id: int
    ws_conn: WsConn
    id: str = ""
    status: t.Optional[SessionStatus] = field(default=None, metadata={"by_value": True})

    @classmethod
    def from_sessiondao(cls, sessiondao: SessionDAO) -> t.Self:
        return cls(
            id=sessiondao.id,
            app_release_uuid=sessiondao.app_release_uuid,
            container=SessionDC.Container.Schema().load(data=sessiondao.container) if sessiondao.container else None,
            status=SessionStatus(sessiondao.status),
            user_id=sessiondao.user_id,
            ws_conn=SessionDC.WsConn.Schema().load(data=sessiondao.ws_conn),
            updated=sessiondao.updated.replace(tzinfo=datetime.timezone.utc),
        )


@dataclass
class CreateSessionRequestDTO:
    @dataclass
    class WsConn:
        """Websocket connection parameters."""

        id: str  # unique ws connection id (used as a sticky session cookie value)
        consumer_id: str  # peer_id of the party awaiting for a stream (UA)
        Schema: t.ClassVar[t.Type[Schema]] = Schema  # pylint: disable=invalid-name

    app_release_uuid: str
    user_id: int
    ws_conn: WsConn
    preferred_dcs: t.Optional[list[str]] = field(default_factory=list)
    Schema: t.ClassVar[t.Type[Schema]] = Schema  # pylint: disable=invalid-name


@dataclass
class CreateSessionResponseDTO:
    session_id: str
    Schema: t.ClassVar[t.Type[Schema]] = Schema  # pylint: disable=invalid-name


@dataclass
class StartSessionRequestDTO:
    @dataclass
    class WsConn:
        id: str  # must be present for `resume` case
        consumer_id: str  # must be present for `resume` case
        producer_id: str

    ws_conn: WsConn
    Schema: t.ClassVar[t.Type[Schema]] = Schema  # pylint: disable=invalid-name


@dataclass
class GetSessionResponseDTO:
    session: SessionDC
    Schema: t.ClassVar[t.Type[Schema]] = Schema  # pylint: disable=invalid-name


@dataclass
class GetSessionsResponseDTO:
    sessions: list[SessionDC]
    Schema: t.ClassVar[t.Type[Schema]] = Schema  # pylint: disable=invalid-name


@dataclass
class SubmitWebRtcStatsRequestDTO:
    stats: str  # json-encoded stats structure
    Schema: t.ClassVar[t.Type[Schema]] = Schema  # pylint: disable=invalid-name
