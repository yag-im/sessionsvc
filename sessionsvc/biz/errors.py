import json
import logging
import typing as t

from flask import (
    Flask,
    Response,
)
from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException

ERROR_APPSVC = (1409, "appsvc exception")
ERROR_SESSION_NOT_FOUND = (1404, "session not found")
ERROR_SESSION_OP = (1409, "session operational error")
ERROR_SESSIONS_QUOTA_LIMIT_EXCEEDED = (1429, "sessions quota limit exceeded for user")
ERROR_UNKNOWN = (1500, "unknown error")

log = logging.getLogger("sessionsvc")


class BizException(Exception):
    def __init__(self, code: t.Optional[int] = None, message: t.Optional[t.Any] = None) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


class SessionOpException(BizException):
    def __init__(self, message: t.Optional[t.Any] = None) -> None:
        code = ERROR_SESSION_OP[0]
        message = message or ERROR_SESSION_OP[1]
        super().__init__(code, message)


class SessionNotFoundException(BizException):
    def __init__(self) -> None:
        code = ERROR_SESSION_NOT_FOUND[0]
        message = ERROR_SESSION_NOT_FOUND[1]
        super().__init__(code, message)


class SessionsQuotaLimitExceededException(BizException):
    def __init__(self) -> None:
        code = ERROR_SESSIONS_QUOTA_LIMIT_EXCEEDED[0]
        message = ERROR_SESSIONS_QUOTA_LIMIT_EXCEEDED[1]
        super().__init__(code, message)


class AppSvcException(BizException):
    def __init__(self, message: t.Optional[t.Any] = None) -> None:
        code = ERROR_APPSVC[0]
        message = message or ERROR_APPSVC[1]
        super().__init__(code, message)


def init_app(app: Flask) -> None:
    """Inits error handlers.

    Make sure FLASK_PROPAGATE_EXCEPTIONS is set to `true`, otherwise errorhandlers will be unreachable.
    """

    @app.errorhandler(Exception)
    def handle_exception(e: Exception) -> Response:
        if isinstance(e, HTTPException):
            return e
        res = json.dumps({"code": ERROR_UNKNOWN[0], "message": ERROR_UNKNOWN[1]})
        log.exception(e)
        return Response(res, mimetype="application/json", status=500)

    @app.errorhandler(ValidationError)
    def handle_validation_error(e: ValidationError) -> Response:
        res = json.dumps(
            {
                "code": 1400,
                "message": e.messages,
            }
        )
        log.error(res)
        return Response(res, mimetype="application/json", status=400)

    @app.errorhandler(BizException)
    def handle_biz_exception(e: BizException) -> Response:
        res = json.dumps(
            {
                "code": e.code,
                "message": e.message,
            }
        )
        log.error(res)
        return Response(res, mimetype="application/json", status=409)
