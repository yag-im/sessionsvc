# sync with appsvc (appsvc/biz/dto.py)

import datetime
import typing as t
from dataclasses import field
from enum import StrEnum

from marshmallow import (
    Schema,
    validate,
)
from marshmallow_dataclass import dataclass


class DcRegion(StrEnum):
    EU_CENTRAL_1 = "eu-central-1"
    US_EAST_1 = "us-east-1"
    US_WEST_1 = "us-west-1"


class WindowSystem(StrEnum):
    X11 = "x11"
    WAYLAND = "wayland"


@dataclass
class ContainerOpDescr:
    id: str
    node_id: str


@dataclass
class ContainerDescr(ContainerOpDescr):
    region: DcRegion = field(metadata={"by_value": True})


@dataclass
class WsConnDC:
    id: str
    consumer_id: str


@dataclass
class AppReleaseDetails:
    @dataclass
    class Company:
        id: int
        name: str
        developer: bool
        porting: bool
        publisher: bool
        supporting: bool

    @dataclass
    class MediaAssets:
        @dataclass
        class Cover:
            image_id: str

        @dataclass
        class Screenshot:
            width: int
            height: int
            image_id: str

        cover: Cover
        screenshots: t.Optional[list[Screenshot]]
        Schema: t.ClassVar[t.Type[Schema]] = Schema  # pylint: disable=invalid-name

    @dataclass
    class Runner:
        name: str
        ver: t.Optional[str]
        window_system: t.Optional[WindowSystem] = field(default=None, metadata={"by_value": True})
        Schema: t.ClassVar[t.Type[Schema]] = Schema  # pylint: disable=invalid-name

    @dataclass
    class AppReqs:
        @dataclass
        class HwReqs:
            dgpu: bool = False
            igpu: bool = False
            memory: int = 0
            memory_shared: int = 0
            nanocpus: int = 0

        @dataclass
        class UaReqs:
            lock_pointer: bool = False

        color_bits: t.Optional[int]
        screen_width: int
        screen_height: int
        hw: HwReqs = field(default_factory=HwReqs)
        midi: bool = False
        ua: UaReqs = field(default_factory=UaReqs)
        Schema: t.ClassVar[t.Type[Schema]] = Schema  # pylint: disable=invalid-name

    @dataclass
    class GameRefs:
        ag_id: t.Optional[int]
        lutris_id: t.Optional[str]
        mg_id: t.Optional[int]
        pcgw_id: t.Optional[str]
        qz_id: t.Optional[int]
        Schema: t.ClassVar[t.Type[Schema]] = Schema  # pylint: disable=invalid-name

    @dataclass
    class IgdbDescr:
        id: int
        slug: str
        similar_ids: t.Optional[list[int]]
        Schema: t.ClassVar[t.Type[Schema]] = Schema  # pylint: disable=invalid-name

    @dataclass
    class AppPlatform:
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
    media_assets_localized: t.Optional[MediaAssets]
    name: str
    platform: AppPlatform
    refs: GameRefs
    runner: Runner
    short_descr: str
    ts_added: datetime.datetime
    uuid: str
    year_released: int


@dataclass
class GetAppReleaseResponseDTO(AppReleaseDetails):
    Schema: t.ClassVar[t.Type[Schema]] = Schema  # pylint: disable=invalid-name


@dataclass
class RunAppRequestDTO:
    app_release_uuid: str
    user_id: int
    ws_conn: WsConnDC
    preferred_dcs: t.Optional[list[str]] = field(default_factory=list)
    Schema: t.ClassVar[t.Type[Schema]] = Schema  # pylint: disable=invalid-name


@dataclass
class RunAppResponseDTO:
    container: ContainerDescr
    Schema: t.ClassVar[t.Type[Schema]] = Schema  # pylint: disable=invalid-name


@dataclass
class PauseAppRequestDTO:
    container: ContainerOpDescr
    Schema: t.ClassVar[t.Type[Schema]] = Schema  # pylint: disable=invalid-name


@dataclass
class ResumeAppRequestDTO:
    container: ContainerOpDescr
    ws_conn: WsConnDC
    Schema: t.ClassVar[t.Type[Schema]] = Schema  # pylint: disable=invalid-name


@dataclass
class StopAppRequestDTO:
    container: ContainerOpDescr
    Schema: t.ClassVar[t.Type[Schema]] = Schema  # pylint: disable=invalid-name


class SearchAppsOrderBy(StrEnum):
    TS_ADDED = "ts_added"
    YEAR_RELEASED = "year_released"
    NAME = "name"


@dataclass
class SearchAppsRequestDTO:
    app_name: t.Optional[str] = field(default=None, metadata={"validate": validate.Length(min=3)})
    kids_mode: bool = False
    offset: int = 0
    limit: int = 100
    order_by: SearchAppsOrderBy = SearchAppsOrderBy.TS_ADDED
    Schema: t.ClassVar[t.Type[Schema]] = Schema  # pylint: disable=invalid-name


@dataclass
class SearchAppsResponseItem:
    cover_image_id: str
    esrb_rating: int
    lang: str
    name: str
    uuid: str
    year_released: int


@dataclass
class SearchAppsResponseDTO:
    apps: t.List[SearchAppsResponseItem] = field(default_factory=list)
    Schema: t.ClassVar[t.Type[Schema]] = Schema  # pylint: disable=invalid-name


@dataclass
class SearchAppsAclRequestDTO:
    app_name: t.Optional[str] = field(default=None, metadata={"validate": validate.Length(min=3)})
    company_name: t.Optional[str] = field(default=None, metadata={"validate": validate.Length(min=3)})
    kids_mode: bool = False
    Schema: t.ClassVar[t.Type[Schema]] = Schema  # pylint: disable=invalid-name


@dataclass
class SearchAppsAclResponseDTO:
    acl: list[str]
    Schema: t.ClassVar[t.Type[Schema]] = Schema  # pylint: disable=invalid-name
