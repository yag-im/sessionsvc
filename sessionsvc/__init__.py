import json
import logging
import os

from fastapi import FastAPI
from sqlalchemy import URL

from sessionsvc.api import router
from sessionsvc.biz import (
    errors,
    log,
)
from sessionsvc.biz.sqldb import (
    SessionScopeMiddleware,
    sqldb,
)


def create_app() -> FastAPI:
    log.init_logging()

    sqldb.init_app(
        URL.create(
            "postgresql+psycopg",
            username=os.environ["SQLDB_USERNAME"],
            password=os.environ["SQLDB_PASSWORD"],
            host=os.environ["SQLDB_HOST"],
            port=int(os.environ["SQLDB_PORT"]),
            database=os.environ["SQLDB_DBNAME"],
        ),
        json.loads(os.environ.get("SQLDB_ENGINE_OPTIONS", "{}")),
    )

    app = FastAPI(title="sessionsvc")
    app.include_router(router)
    app.add_middleware(SessionScopeMiddleware)
    errors.init_app(app)

    logging.getLogger("sessionsvc").info("app init completed")

    # import logging
    # logging.basicConfig()
    # logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

    return app
