import datetime
import typing as t
from enum import StrEnum

from pydantic import (
    BaseModel,
    Field,
    PlainSerializer,
)

from sessionsvc.biz.models import SessionDAO
from sessionsvc.services.dto.appsvc import DcRegion
from sessionsvc.services.dto.types import EnumByName

# keep the `+00:00` offset format (pydantic would emit `Z`)
IsoDateTime = t.Annotated[
    datetime.datetime, PlainSerializer(lambda d: d.isoformat(), return_type=str, when_used="json")
]


class SessionStatus(StrEnum):
    PENDING = "pending"
    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"


class SessionDC(BaseModel):
    class WsConn(BaseModel):
        """Websocket connection parameters."""

        id: str  # unique ws connection id (used as a sticky session cookie value)
        consumer_id: str  # peer_id of the party awaiting for a stream (UA)
        producer_id: t.Optional[str] = None  # peer_id of the party producing a stream (streamd)

    class Container(BaseModel):
        """Docker container parameters."""

        id: str
        node_id: str
        # stored in sessions.container (and exposed via API) by enum name, e.g. "US_EAST_1"
        region: t.Annotated[DcRegion, EnumByName()]
        cpuset_cpus: list[int]

    app_release_uuid: str
    container: t.Optional[Container] = None
    updated: IsoDateTime
    user_id: int
    ws_conn: WsConn
    id: str = ""
    status: t.Optional[SessionStatus] = None

    @classmethod
    def from_sessiondao(cls, sessiondao: SessionDAO) -> t.Self:
        return cls(
            id=sessiondao.id,
            app_release_uuid=sessiondao.app_release_uuid,
            container=SessionDC.Container.model_validate(sessiondao.container) if sessiondao.container else None,
            status=SessionStatus(sessiondao.status),
            user_id=sessiondao.user_id,
            ws_conn=SessionDC.WsConn.model_validate(sessiondao.ws_conn),
            updated=sessiondao.updated.replace(tzinfo=datetime.timezone.utc),
        )


class CreateSessionRequestDTO(BaseModel):
    class WsConn(BaseModel):
        """Websocket connection parameters."""

        id: str  # unique ws connection id (used as a sticky session cookie value)
        consumer_id: str  # peer_id of the party awaiting for a stream (UA)

    app_release_uuid: str
    user_id: int
    ws_conn: WsConn
    preferred_dcs: t.Optional[list[str]] = Field(default_factory=list)


class CreateSessionResponseDTO(BaseModel):
    session_id: str


class StartSessionRequestDTO(BaseModel):
    class WsConn(BaseModel):
        id: str  # must be present for `resume` case
        consumer_id: str  # must be present for `resume` case
        producer_id: str

    ws_conn: WsConn


class GetSessionResponseDTO(BaseModel):
    session: SessionDC


class GetSessionsResponseDTO(BaseModel):
    sessions: list[SessionDC]


class SubmitWebRtcStatsRequestDTO(BaseModel):
    stats: str  # json-encoded stats structure
