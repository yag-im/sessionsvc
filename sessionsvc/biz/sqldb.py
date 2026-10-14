import threading
import typing as t
from contextvars import ContextVar

from sqlalchemy import (
    URL,
    create_engine,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    scoped_session,
    sessionmaker,
)
from starlette.concurrency import run_in_threadpool
from starlette.types import (
    ASGIApp,
    Receive,
    Scope,
    Send,
)

_request_scope: ContextVar[object | None] = ContextVar("sqldb_request_scope", default=None)


def _scopefunc() -> object:
    # contextvars propagate into the threadpool running sync endpoints; fall back to thread outside requests
    return _request_scope.get() or threading.get_ident()


class Model(DeclarativeBase):
    pass


class SQLDB:
    Model = Model

    def __init__(self) -> None:
        self.session = scoped_session(sessionmaker(), scopefunc=_scopefunc)

    def init_app(self, url: URL, engine_options: dict[str, t.Any]) -> None:
        self.session.configure(bind=create_engine(url, **engine_options))


sqldb = SQLDB()


class SessionScopeMiddleware:
    """Provides one db session per request and releases it when the request is done."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        token = _request_scope.set(object())
        try:
            await self.app(scope, receive, send)
        finally:
            await run_in_threadpool(sqldb.session.remove)
            _request_scope.reset(token)
