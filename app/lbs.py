# -*- coding:utf-8 -*-
from apscheduler.schedulers.background import BackgroundScheduler     # Apscheduler ver 3.3.1
from datetime import datetime
import urllib2
import json
from models import HzToken, HzLocation
from app import db
import random
import logging

log = logging.getLogger('apscheduler.executors.default')
log.setLevel(logging.WARNING)

fmt = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
h = logging.StreamHandler()
h.setFormatter(fmt)
log.addHandler(h)

HZ_LICENSE = "cb5537fd8e684827b7e4f83b742c8f2c"
JOB_INTERVAL = 2                      # seconds
TEST_UID = "1918E00103AA"           # 测试用标签UID
TEST_UID_2 = "1918E00103A9"         # 测试用标签UID
GEO_SCALE = 0.0891                    # 像素坐标(px) * 10 / 物理坐标(mm) = 89.1%
CUR_MAP_SCALE = 0.3                     # 当前屏幕地图缩放比例 30%
HZ_MAP_GEO_WIDTH = 39023.569023569024   # 毫米
HZ_MAP_GEO_HEIGHT = 19854.09652076319
# [{"name":"Floor3","mapImage":"Floor3.jpg","mapImageWidth":3477,"mapImageHeight":1769,"geoScale":{"x":89.1,"y":89.1}}]
HZ_TEST_ADD_POS = False                 # 为真，则向数据库随机插入坐标点
HZ_UID = [TEST_UID, TEST_UID_2]


def job_get_token():
    time_now = datetime.utcnow()
    hz_token = HzToken.query.all()
    dt_time = (time_now - hz_token[0].timestamp).total_seconds()
    if len(hz_token) > 0 and dt_time < hz_token[0].expires_in - JOB_INTERVAL - 60 * 10:
        get_location(hz_token[0].token)
        return

    test_data = {"licence": HZ_LICENSE}
    url = "https://api.joysuch.com:46000/getAccessTokenV2"

    # refresh access token
    if len(hz_token) == 0:
        url = "https://api.joysuch.com:46000/refreshAccessToken"
        test_data = {"refreshToken": hz_token[0].refresh_token}

    data = json.dumps(test_data)
    headers = {'Content-Type': 'application/json;charset=UTF-8'}
    req = urllib2.Request(url=url, data=data, headers=headers)
    res_data = urllib2.urlopen(req)
    res = res_data.read()
    obj = json.loads(res)
    if obj['errorCode'] == 0:
        if len(hz_token) == 0:      # 还没有获取过token
            my_token = HzToken(license=HZ_LICENSE,
                               token=obj['data']['token'],
                               refresh_token=obj['data']['refreshToken'],
                               expires_in=obj['data']['expiresIn'],
                               timestamp=datetime.utcnow())
            db.session.add(my_token)
            db.session.commit()
        else:           # 更新token
            hz_token[0].token = obj['data']['token']
            hz_token[0].refresh_token = obj['data']['refreshToken']
            hz_token[0].expires_in = obj['data']['expiresIn']
            hz_token[0].timestamp = time_now
            print "Update token:", hz_token[0], "at", time_now, "[END]"
            db.session.add(hz_token[0])
            db.session.commit()
        # get_location(obj['data']['token'])
    else:
        print "error in function job_get_token(): ", res
        print "url= ", url
        print "req data= ", test_data
        return


def get_location(token):
    url = "https://api.joysuch.com:46000/WebLocate/locateResults"
    data = {'accessToken': token,
            'userIds': HZ_UID,
            'timePeriod': 3000}
    headers = {'Content-Type': 'application/json;charset=UTF-8'}
    req = urllib2.Request(url=url, data=json.dumps(data), headers=headers)
    res_data = urllib2.urlopen(req)
    res = res_data.read()
    obj = json.loads(res)
    if obj["errorCode"] == 0:
        # 测试代码。向数据库随机插入坐标点
        if HZ_TEST_ADD_POS:
            test_loc = HzLocation(build_id='', floor_no='', user_id=TEST_UID,
                                  x=random.randint(20, int(HZ_MAP_GEO_WIDTH)-1000),
                                  y=random.randint(20, int(HZ_MAP_GEO_HEIGHT)-1000),
                                  timestamp=datetime.today())
            db.session.add(test_loc)
            db.session.commit()
        for item in obj["data"]:
            hz_location = HzLocation(build_id=item["buildId"],
                                     floor_no=item["floorNo"],
                                     user_id=item["userId"],
                                     x=item["xMillimeter"],
                                     y=item["yMillimeter"],
                                     timestamp=datetime.today())
            db.session.add(hz_location)
            db.session.commit()
    else:
        print "error in function get_location(): ", res
        print "url= ", url
        print "req data= ", data

    return


scheduler = BackgroundScheduler()
scheduler.add_job(job_get_token, 'interval', seconds=JOB_INTERVAL, id='my_job_get_token',
                  next_run_time=datetime.now())

scheduler.start()
