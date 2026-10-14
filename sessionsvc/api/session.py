from fastapi import APIRouter

from sessionsvc.biz import session as session_biz
from sessionsvc.biz.dto import (
    CreateSessionRequestDTO,
    CreateSessionResponseDTO,
    GetSessionResponseDTO,
    GetSessionsResponseDTO,
    StartSessionRequestDTO,
    SubmitWebRtcStatsRequestDTO,
)
from sessionsvc.biz.stats import submit_webrtc_stats

router = APIRouter()


@router.post("/sessions/create")
def create_session(req: CreateSessionRequestDTO) -> CreateSessionResponseDTO:
    """Creates a new session."""

    return session_biz.create_session(req)


@router.post("/sessions/{session_id}/start")
def start_session(session_id: str, req: StartSessionRequestDTO) -> str:
    """Starts a new or resumes a paused session."""

    session_biz.start_session(session_id, req)
    return ""


@router.post("/sessions/{session_id}/pause")
def pause_session(session_id: str) -> str:
    """Pauses an active session."""

    session_biz.pause_session(session_id)
    return ""


@router.post("/sessions/{session_id}/close")
def close_session(session_id: str) -> str:
    """Closes and removes session."""

    session_biz.close_session(session_id)
    return ""


@router.post("/sessions/{session_id}/stats")
def submit_stats(session_id: str, req: SubmitWebRtcStatsRequestDTO) -> str:
    """Submit webrtc stats for a given session."""

    submit_webrtc_stats(session_id, req)
    return ""


@router.get("/sessions/{session_id}")
def get_session(session_id: str) -> GetSessionResponseDTO:
    """Get existing session."""

    return GetSessionResponseDTO(session=session_biz.get_session(session_id))


@router.get("/sessions")
def get_sessions(node_id: str | None = None) -> GetSessionsResponseDTO:
    """Get all sessions."""

    return GetSessionsResponseDTO(sessions=session_biz.get_sessions(node_id=node_id))


@router.get("/consumers/{consumer_id}/sessions")
def get_consumer_sessions(consumer_id: str) -> GetSessionsResponseDTO:
    """Get consumer sessions."""

    return GetSessionsResponseDTO(sessions=session_biz.get_consumer_sessions(consumer_id))


@router.get("/producers/{producer_id}/sessions")
def get_producer_sessions(producer_id: str) -> GetSessionsResponseDTO:
    """Get producer sessions."""

    return GetSessionsResponseDTO(sessions=session_biz.get_producer_sessions(producer_id))


@router.get("/users/{user_id}/sessions")
def get_user_sessions(user_id: int) -> GetSessionsResponseDTO:
    """Get user sessions."""

    return GetSessionsResponseDTO(sessions=session_biz.get_user_sessions(user_id))
