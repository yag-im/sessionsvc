from flask_restful import Api

from sessionsvc.api.session import (
    CloseSession,
    CreateSession,
    GetConsumerSessions,
    GetProducerSessions,
    GetSession,
    GetSessions,
    GetUserSessions,
    PauseSession,
    StartSession,
    SubmitWebRtcStats,
)

api = Api()

# setup routing
api.add_resource(CreateSession, "/sessions/create")  # POST
api.add_resource(StartSession, "/sessions/<string:session_id>/start")  # POST
api.add_resource(PauseSession, "/sessions/<string:session_id>/pause")  # POST
api.add_resource(CloseSession, "/sessions/<string:session_id>/close")  # POST
api.add_resource(SubmitWebRtcStats, "/sessions/<string:session_id>/stats")  # POST

api.add_resource(GetSession, "/sessions/<string:session_id>")  # GET
api.add_resource(GetSessions, "/sessions")  # GET
api.add_resource(GetConsumerSessions, "/consumers/<string:consumer_id>/sessions")  # GET
api.add_resource(GetProducerSessions, "/producers/<string:producer_id>/sessions")  # GET
api.add_resource(GetUserSessions, "/users/<string:user_id>/sessions")  # GET
