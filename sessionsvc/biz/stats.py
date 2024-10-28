import json
from collections import deque

from sessionsvc.biz.dto import SubmitWebRtcStatsRequestDTO
from sessionsvc.biz.models import (
    UsersDcsDAO,
    WebRTCStatsLogsDAO,
)
from sessionsvc.biz.session import get_session
from sessionsvc.biz.sqldb import sqldb

MAX_RTTS = 100


def submit_webrtc_stats(session_id: str, req: SubmitWebRtcStatsRequestDTO) -> None:
    """Submit webrtc stats.

    Create a new entry in the stats.webrtc_stats_logs table;
    Update dcs in the stats.users_dcs (recording only best rtt per region);
    """
    session = get_session(session_id)
    user_id = session.user_id
    stats = json.loads(req.stats)
    if "remote_inbound_rtp" in stats:
        user_dcs = sqldb.session.query(UsersDcsDAO).filter(UsersDcsDAO.user_id == user_id).first()
        cur_rtt = stats["remote_inbound_rtp"]["round_trip_time"]
        if cur_rtt and (0 < cur_rtt < 5):
            if user_dcs:
                cur_dcs = user_dcs.dcs
                if session.container.region not in cur_dcs:
                    rtts = [cur_rtt]
                else:
                    rtts_dq = deque(cur_dcs[session.container.region], maxlen=MAX_RTTS)
                    rtts_dq.append(cur_rtt)
                    rtts = list(rtts_dq)
                cur_dcs[session.container.region] = rtts
                sqldb.session.query(UsersDcsDAO).filter(UsersDcsDAO.user_id == user_id).update(
                    {
                        UsersDcsDAO.dcs: cur_dcs,
                    }
                )
            else:
                sqldb.session.add(UsersDcsDAO(dcs={session.container.region: [cur_rtt]}, user_id=user_id))

    new_stats_entry = WebRTCStatsLogsDAO(
        app_release_uuid=session.app_release_uuid,
        region=session.container.region,
        session_id=session_id,
        stats=stats,
        user_id=user_id,
    )
    sqldb.session.add(new_stats_entry)

    sqldb.session.commit()
