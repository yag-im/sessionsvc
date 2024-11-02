import os

from flask import Flask

from sessionsvc.api import api
from sessionsvc.biz import (
    errors,
    log,
)
from sessionsvc.biz.sqldb import sqldb


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_prefixed_env()
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f'postgresql://{os.environ["SQLDB_USERNAME"]}:{os.environ["SQLDB_PASSWORD"]}@{os.environ["SQLDB_HOST"]}:\
        {os.environ["SQLDB_PORT"]}/{os.environ["SQLDB_DBNAME"]}'
    )

    # init extensions
    api.init_app(app)
    sqldb.init_app(app)
    errors.init_app(app)
    log.init_app(app)

    app.logger.info("app init completed")

    # import logging
    # logging.basicConfig()
    # logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

    return app
