import logging
import typing as t
import uuid
from dataclasses import (
    dataclass,
    field,
)

from sqlalchemy.exc import IntegrityError

import sessionsvc.services.dto.appsvc as dto_appsvc
from sessionsvc.biz.dto import (
    CreateSessionRequestDTO,
    CreateSessionResponseDTO,
    SessionDC,
    SessionStatus,
    StartSessionRequestDTO,
)
from sessionsvc.biz.errors import (
    SessionNotFoundException,
    SessionOpException,
    SessionsQuotaLimitExceededException,
)
from sessionsvc.biz.misc import log_input_output
from sessionsvc.biz.models import SessionDAO
from sessionsvc.biz.sqldb import sqldb
from sessionsvc.services import appsvc

log = logging.getLogger("sessionsvc")

# TODO: handle throught the quotas service/table
MAX_USER_SESSIONS = 1


@dataclass
class UpdateSessionDC:
    id: str
    app_release_uuid: t.Optional[str] = None
    container: t.Optional[SessionDC.Container] = None
    status: t.Optional[SessionStatus] = field(metadata={"by_value": True}, default=None)
    user_id: t.Optional[int] = None
    ws_conn: t.Optional[SessionDC.WsConn] = None


def _delete_session(session_id: str) -> None:
    rows_updated = sqldb.session.query(SessionDAO).filter(SessionDAO.id == session_id).delete()
    if rows_updated == 0:
        raise SessionNotFoundException()
    elif rows_updated > 1:
        raise SessionOpException(message="Multiple sessions touched, this is unexpected, please investigate")
    sqldb.session.commit()


def _update_session(session: UpdateSessionDC) -> None:
    upd_params = {}
    if session.status:
        upd_params[SessionDAO.status] = session.status.value
    if session.ws_conn:
        upd_params[SessionDAO.ws_conn] = SessionDC.WsConn.Schema().dump(session.ws_conn)
    if session.container:
        upd_params[SessionDAO.container] = SessionDC.Container.Schema().dump(session.container)
    rows_updated = sqldb.session.query(SessionDAO).filter(SessionDAO.id == session.id).update(upd_params)
    if rows_updated == 0:
        raise SessionNotFoundException()
    elif rows_updated > 1:
        raise SessionOpException(message="Multiple sessions touched, this is unexpected, please investigate")
    sqldb.session.commit()


def _create_session(req: CreateSessionRequestDTO) -> CreateSessionResponseDTO:
    session_id = str(uuid.uuid4())

    # Create a new session object
    new_session = SessionDAO(
        id=session_id,
        app_release_uuid=req.app_release_uuid,
        user_id=req.user_id,
        ws_conn=SessionDC.WsConn.Schema().dump(
            SessionDC.WsConn(
                id=req.ws_conn.id,
                consumer_id=req.ws_conn.consumer_id,
                producer_id=None,
            )
        ),
        status=SessionStatus.PENDING.value,
    )
    sqldb.session.add(new_session)
    sqldb.session.commit()
    return CreateSessionResponseDTO(session_id=session_id)


@log_input_output
def create_session(req: CreateSessionRequestDTO) -> CreateSessionResponseDTO:
    user_sessions = get_user_sessions(req.user_id)
    if len(user_sessions) > MAX_USER_SESSIONS:
        raise SessionsQuotaLimitExceededException
    for session in user_sessions:
        if session.app_release_uuid == req.app_release_uuid:
            if session.status != SessionStatus.PAUSED:
                # possible causes:
                #   - "fast-click": same app was quickly started more than once
                #   - same app was requested to be run in a new tab
                raise SessionOpException(f"found existing session in a non-paused state (id: {session.id})")
            # updating session primarily to reset old ws_conn.producer_id so it couldn't control resumed session
            # consumer_id and id may be also switched in a session resume flow
            _update_session(
                UpdateSessionDC(
                    id=session.id,
                    status=SessionStatus.PENDING,
                    ws_conn=SessionDC.WsConn(
                        id=req.ws_conn.id,
                        consumer_id=req.ws_conn.consumer_id,
                    ),
                )
            )
            appsvc.resume_app(
                dto_appsvc.ResumeAppRequestDTO(
                    container=dto_appsvc.ContainerOpDescr(
                        id=session.container.id,
                        node_id=session.container.node_id,
                    ),
                    ws_conn=dto_appsvc.WsConnDC(
                        id=req.ws_conn.id,
                        consumer_id=req.ws_conn.consumer_id,
                    ),
                )
            )
            # start_session (resume) will be called later, from sigsvc
            return CreateSessionResponseDTO(session_id=session.id)
    if len(user_sessions) >= MAX_USER_SESSIONS:
        raise SessionsQuotaLimitExceededException

    # _create_session must be called before the run_app to avoid dup sessions (sessions.user_id is a unique key)
    # container params will be set after successfull execution of the run_app
    # producer_id will be set later from the start_session call
    try:
        create_sess_res = _create_session(req)
        run_app_res: dto_appsvc.RunAppResponseDTO = appsvc.run_app(
            dto_appsvc.RunAppRequestDTO(
                app_release_uuid=req.app_release_uuid,
                user_id=req.user_id,
                preferred_dcs=req.preferred_dcs,
                ws_conn=dto_appsvc.WsConnDC(id=req.ws_conn.id, consumer_id=req.ws_conn.consumer_id),
            )
        )
        # now setting container attributes
        _update_session(
            UpdateSessionDC(
                id=create_sess_res.session_id,
                container=SessionDC.Container(
                    run_app_res.container.id,
                    node_id=run_app_res.container.node_id,
                    region=run_app_res.container.region,
                ),
            )
        )
        return create_sess_res
    except IntegrityError as e:
        raise SessionsQuotaLimitExceededException from e


@log_input_output
def pause_session(session_id: str) -> None:
    session: SessionDC = get_session(session_id)
    if not session.container:
        raise SessionOpException(message="session.container is empty")
    appsvc.pause_app(
        dto_appsvc.PauseAppRequestDTO(
            container=dto_appsvc.ContainerOpDescr(
                id=session.container.id,
                node_id=session.container.node_id,
            )
        )
    )
    _update_session(UpdateSessionDC(id=session_id, status=SessionStatus.PAUSED))


@log_input_output
def start_session(session_id: str, req: StartSessionRequestDTO) -> None:
    session: SessionDC = get_session(session_id)
    session.ws_conn.producer_id = req.ws_conn.producer_id
    _update_session(
        UpdateSessionDC(
            id=session_id,
            status=SessionStatus.ACTIVE,
            ws_conn=session.ws_conn,
        )
    )
    # in case session was in a PAUSED state, app will resume as part of the "create_session" call


@log_input_output
def close_session(session_id: str) -> None:
    try:
        session: SessionDC = get_session(session_id)
        if session.status in {SessionStatus.PAUSED, SessionStatus.ACTIVE} and session.container:
            appsvc.stop_app(
                dto_appsvc.StopAppRequestDTO(
                    container=dto_appsvc.ContainerOpDescr(
                        id=session.container.id,
                        node_id=session.container.node_id,
                    )
                )
            )
        _delete_session(session_id)
    except SessionNotFoundException:
        log.warning("session %s was already closed", session_id)


@log_input_output
def get_session(session_id: str) -> SessionDC:
    session = sqldb.session.query(SessionDAO).filter(SessionDAO.id == session_id).first()
    if not session:
        raise SessionNotFoundException
    return SessionDC.from_sessiondao(session)


@log_input_output
def get_user_sessions(user_id: int) -> list[SessionDC]:
    sessions = sqldb.session.query(SessionDAO).filter(SessionDAO.user_id == user_id).all()
    return [SessionDC.from_sessiondao(s) for s in sessions]


@log_input_output
def get_consumer_sessions(consumer_id: str) -> list[SessionDC]:
    sessions = sqldb.session.query(SessionDAO).filter(SessionDAO.ws_conn["consumer_id"].astext == consumer_id).all()
    return [SessionDC.from_sessiondao(s) for s in sessions]


@log_input_output
def get_producer_sessions(producer_id: str) -> list[SessionDC]:
    sessions = sqldb.session.query(SessionDAO).filter(SessionDAO.ws_conn["producer_id"].astext == producer_id).all()
    return [SessionDC.from_sessiondao(s) for s in sessions]


def get_sessions() -> list[SessionDC]:
    sessions = sqldb.session.query(SessionDAO).all()
    return [SessionDC.from_sessiondao(s) for s in sessions]
