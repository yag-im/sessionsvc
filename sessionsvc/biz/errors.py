import logging
import typing as t

from fastapi import (
    FastAPI,
    Request,
)
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

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


def init_app(app: FastAPI) -> None:
    """Inits error handlers."""

    @app.exception_handler(Exception)
    async def handle_exception(_: Request, e: Exception) -> JSONResponse:
        log.exception(e)
        return JSONResponse({"code": ERROR_UNKNOWN[0], "message": ERROR_UNKNOWN[1]}, status_code=500)

    @app.exception_handler(ValidationError)
    async def handle_validation_error(_: Request, e: ValidationError) -> JSONResponse:
        res = {"code": 1400, "message": jsonable_encoder(e.errors(include_url=False))}
        log.error(res)
        return JSONResponse(res, status_code=400)

    @app.exception_handler(RequestValidationError)
    async def handle_request_validation_error(_: Request, e: RequestValidationError) -> JSONResponse:
        res = {"code": 1400, "message": jsonable_encoder(e.errors())}
        log.error(res)
        return JSONResponse(res, status_code=400)

    @app.exception_handler(BizException)
    async def handle_biz_exception(_: Request, e: BizException) -> JSONResponse:
        res = {"code": e.code, "message": e.message}
        log.error(res)
        return JSONResponse(res, status_code=409)
