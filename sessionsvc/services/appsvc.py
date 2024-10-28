import json
import logging
import os

from sessionsvc.biz.errors import AppSvcException
from sessionsvc.services.dto.appsvc import (
    PauseAppRequestDTO,
    ResumeAppRequestDTO,
    RunAppRequestDTO,
    RunAppResponseDTO,
    StopAppRequestDTO,
)
from sessionsvc.services.helpers import get_http_client_session

APPSVC_URL = os.environ["APPSVC_URL"]
REQUESTS_TIMEOUT_CONN_READ = (3, 10)

log = logging.getLogger("sessionsvc.appsvc")


def run_app(req: RunAppRequestDTO) -> RunAppResponseDTO:
    s = get_http_client_session()
    try:
        res = s.post(
            url=f"{APPSVC_URL}/apps/run",
            data=json.dumps(RunAppRequestDTO.Schema().dump(req)),
            headers={"Content-Type": "application/json"},
            timeout=(3, 55),
        )
        if res.status_code != 200:
            raise AppSvcException(res.text)
        return RunAppResponseDTO.Schema().load(data=res.json())
    except Exception as e:
        log.exception(e)
        if isinstance(e, AppSvcException):
            raise e
        raise AppSvcException from e


def pause_app(req: PauseAppRequestDTO) -> None:
    s = get_http_client_session()
    try:
        res = s.post(
            url=f"{APPSVC_URL}/apps/pause",
            data=json.dumps(PauseAppRequestDTO.Schema().dump(req)),
            headers={"Content-Type": "application/json"},
            timeout=REQUESTS_TIMEOUT_CONN_READ,
        )
        if res.status_code != 200:
            raise AppSvcException(res.text)
    except Exception as e:
        log.exception(e)
        if isinstance(e, AppSvcException):
            raise e
        raise AppSvcException from e


def resume_app(req: ResumeAppRequestDTO) -> None:
    s = get_http_client_session()
    try:
        res = s.post(
            url=f"{APPSVC_URL}/apps/resume",
            data=json.dumps(ResumeAppRequestDTO.Schema().dump(req)),
            headers={"Content-Type": "application/json"},
            timeout=REQUESTS_TIMEOUT_CONN_READ,
        )
        if res.status_code != 200:
            raise AppSvcException(res.text)
    except Exception as e:
        log.exception(e)
        if isinstance(e, AppSvcException):
            raise e
        raise AppSvcException from e


def stop_app(req: StopAppRequestDTO) -> None:
    s = get_http_client_session()
    try:
        res = s.post(
            url=f"{APPSVC_URL}/apps/stop",
            data=json.dumps(StopAppRequestDTO.Schema().dump(req)),
            headers={"Content-Type": "application/json"},
            timeout=REQUESTS_TIMEOUT_CONN_READ,
        )
        if res.status_code != 200:
            raise AppSvcException(res.text)
    except Exception as e:
        log.exception(e)
        if isinstance(e, AppSvcException):
            raise e
        raise AppSvcException from e
