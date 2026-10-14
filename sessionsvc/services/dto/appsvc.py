# sync with appsvc (appsvc/biz/dto.py)

import datetime
import typing as t
from enum import StrEnum

from pydantic import (
    BaseModel,
    Field,
)

from sessionsvc.services.dto.types import EnumByName


class DcRegion(StrEnum):
    EU_CENTRAL_1 = "eu-central-1"
    US_EAST_1 = "us-east-1"
    US_WEST_1 = "us-west-1"


class WindowSystem(StrEnum):
    X11 = "x11"
    WAYLAND = "wayland"


class ContainerOpDescr(BaseModel):
    id: str
    node_id: str


class ContainerDescr(ContainerOpDescr):
    region: DcRegion
    cpuset_cpus: list[int]


class WsConnDC(BaseModel):
    id: str
    consumer_id: str


class GpuModel(StrEnum):
    INTEL_UHD_P630 = "intel-uhd-p630"  # RISE-3
    INTEL_UHD_750 = "intel-uhd-750"  # PC-CUSTOM-1
    NVIDIA_GTX_1060 = "nvidia-gtx-1060"  # PC-CUSTOM-1
    NVIDIA_TESLA_V100S = "nvidia-tesla-v100s"  # OVH t2-*
    NVIDIA_L4 = "nvidia-l4"  # OVH l4-*


class AppReleaseDetails(BaseModel):
    class Company(BaseModel):
        id: int
        name: str
        developer: bool
        porting: bool
        publisher: bool
        supporting: bool

    class MediaAssets(BaseModel):
        class Cover(BaseModel):
            image_id: str

        class Screenshot(BaseModel):
            width: int
            height: int
            image_id: str

        cover: Cover
        screenshots: t.Optional[list[Screenshot]] = None

    class Runner(BaseModel):
        name: str
        ver: t.Optional[str] = None
        window_system: t.Optional[WindowSystem] = None

    class AppReqs(BaseModel):
        class HwReqs(BaseModel):
            gpu: t.Annotated[GpuModel, EnumByName()] | None = None
            memory: int = 0
            memory_shared: int = 0
            nanocpus: int = 0

        class UaReqs(BaseModel):
            lock_pointer: bool = False

        color_bits: t.Optional[int] = None
        screen_width: int
        screen_height: int
        hw: HwReqs = Field(default_factory=HwReqs)
        midi: bool = False
        ua: UaReqs = Field(default_factory=UaReqs)
        loading_duration: t.Optional[int] = 0

    class GameRefs(BaseModel):
        ag_id: t.Optional[int] = None
        lutris_id: t.Optional[str] = None
        mg_id: t.Optional[int] = None
        pcgw_id: t.Optional[str] = None
        qz_id: t.Optional[int] = None

    class IgdbDescr(BaseModel):
        id: int
        slug: str
        similar_ids: t.Optional[list[int]] = None

    class AppPlatform(BaseModel):
        id: int
        name: str
        abbreviation: str
        alternative_name: str
        slug: str

    addl_artifacts: dict
    alternative_names: list[str]
    app_reqs: AppReqs
    companies: list[Company]
    esrb_rating: int
    igdb: IgdbDescr
    is_visible: bool
    lang: str
    long_descr: str
    media_assets: MediaAssets
    media_assets_localized: t.Optional[MediaAssets] = None
    name: str
    platform: AppPlatform
    refs: GameRefs
    runner: Runner
    short_descr: str
    ts_added: datetime.datetime
    uuid: str
    year_released: int
    tags: list[str] | None = None


class GetAppReleaseResponseDTO(AppReleaseDetails):
    pass


class RunAppRequestDTO(BaseModel):
    app_release_uuid: str
    user_id: int
    ws_conn: WsConnDC
    preferred_dcs: t.Optional[list[str]] = Field(default_factory=list)


class RunAppResponseDTO(BaseModel):
    container: ContainerDescr


class PauseAppRequestDTO(BaseModel):
    container: ContainerOpDescr


class ResumeAppRequestDTO(BaseModel):
    container: ContainerOpDescr
    ws_conn: WsConnDC


class StopAppRequestDTO(BaseModel):
    container: ContainerOpDescr


class SearchAppsOrderBy(StrEnum):
    TS_ADDED = "ts_added"
    YEAR_RELEASED = "year_released"
    NAME = "name"


class SearchAppsRequestDTO(BaseModel):
    app_name: t.Optional[str] = Field(default=None, min_length=3)
    kids_mode: bool = False
    offset: int = 0
    limit: int = 100
    order_by: t.Annotated[SearchAppsOrderBy, EnumByName()] = SearchAppsOrderBy.TS_ADDED


class SearchAppsResponseItem(BaseModel):
    cover_image_id: str
    esrb_rating: int
    lang: str
    name: str
    uuid: str
    year_released: int
    tags: list[str] | None = None


class SearchAppsResponseDTO(BaseModel):
    apps: list[SearchAppsResponseItem] = Field(default_factory=list)


class SearchAppsAclRequestDTO(BaseModel):
    app_name: t.Optional[str] = Field(default=None, min_length=3)
    company_name: t.Optional[str] = Field(default=None, min_length=3)
    kids_mode: bool = False


class SearchAppsAclResponseDTO(BaseModel):
    acl: list[str]
