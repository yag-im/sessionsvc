from flask import (
    Response,
    request,
)
from flask_restful import Resource

from sessionsvc.biz.dto import (
    CreateSessionRequestDTO,
    CreateSessionResponseDTO,
    GetSessionResponseDTO,
    GetSessionsResponseDTO,
    StartSessionRequestDTO,
    SubmitWebRtcStatsRequestDTO,
)
from sessionsvc.biz.session import (
    close_session,
    create_session,
    get_consumer_sessions,
    get_producer_sessions,
    get_session,
    get_sessions,
    get_user_sessions,
    pause_session,
    start_session,
)
from sessionsvc.biz.stats import submit_webrtc_stats


class CreateSession(Resource):
    def post(self) -> Response:
        """Creates a new session."""

        req: CreateSessionRequestDTO = CreateSessionRequestDTO.Schema().load(data=request.get_json())
        res = create_session(req)
        return CreateSessionResponseDTO.Schema().dump(res), 200


class StartSession(Resource):
    def post(self, session_id: str) -> Response:
        """Starts a new or resumes a paused session."""

        req: StartSessionRequestDTO = StartSessionRequestDTO.Schema().load(data=request.get_json())
        start_session(session_id, req)
        return "", 200


class PauseSession(Resource):
    def post(self, session_id: str) -> Response:
        """Pauses an active session."""

        pause_session(session_id)
        return "", 200


class CloseSession(Resource):
    def post(self, session_id: str) -> Response:
        """Closes and removes session."""

        close_session(session_id)
        return "", 200


class GetSession(Resource):
    def get(self, session_id: str) -> Response:
        """Get existing session."""

        res: GetSessionResponseDTO = GetSessionResponseDTO(session=get_session(session_id))
        return GetSessionResponseDTO.Schema().dump(res), 200


class GetUserSessions(Resource):
    def get(self, user_id: str) -> Response:
        """Get user sessions."""

        res: GetSessionsResponseDTO = GetSessionsResponseDTO(sessions=get_user_sessions(int(user_id)))
        return GetSessionsResponseDTO.Schema().dump(res), 200


class GetConsumerSessions(Resource):
    def get(self, consumer_id: str) -> Response:
        """Get consumer sessions."""

        res: GetSessionsResponseDTO = GetSessionsResponseDTO(sessions=get_consumer_sessions(consumer_id))
        return GetSessionsResponseDTO.Schema().dump(res), 200


class GetProducerSessions(Resource):
    def get(self, producer_id: str) -> Response:
        """Get producer sessions."""

        res: GetSessionsResponseDTO = GetSessionsResponseDTO(sessions=get_producer_sessions(producer_id))
        return GetSessionsResponseDTO.Schema().dump(res), 200


class SubmitWebRtcStats(Resource):
    def post(self, session_id: str) -> Response:
        """Submit webrtc stats for a given session."""

        req: SubmitWebRtcStatsRequestDTO = SubmitWebRtcStatsRequestDTO.Schema().load(data=request.get_json())
        submit_webrtc_stats(session_id, req)
        return "", 200


class GetSessions(Resource):
    def get(self) -> Response:
        """Get all sessions."""

        res: GetSessionsResponseDTO = GetSessionsResponseDTO(sessions=get_sessions())
        return GetSessionsResponseDTO.Schema().dump(res), 200
