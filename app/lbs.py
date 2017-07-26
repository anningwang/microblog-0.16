# -*- coding:utf-8 -*-
from apscheduler.schedulers.background import BackgroundScheduler     # Apscheduler ver 3.3.1
from datetime import datetime
import urllib2
import json
from models import HzToken, HzLocation
from app import db
import logging

log = logging.getLogger('apscheduler.executors.default')
log.setLevel(logging.WARNING)

fmt = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
h = logging.StreamHandler()
h.setFormatter(fmt)
log.addHandler(h)

JOB_INTERVAL = 30       # seconds


def job_get_token():
    time_now = datetime.utcnow()
    hz_token = HzToken.query.all()
    dt_time = (time_now - hz_token[0].timestamp).total_seconds()
    if len(hz_token) > 0 and dt_time < hz_token[0].expires_in - JOB_INTERVAL - 60 * 5:
        return

    license = "cb5537fd8e684827b7e4f83b742c8f2c"
    test_data = {"licence": license}
    url = "https://api.joysuch.com:46000/getAccessTokenV2"
    # refresh access token
    if len(hz_token) > 0 and (time_now - hz_token[0].timestamp).total_seconds() < hz_token[0].expires_in:
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
            my_token = HzToken(license=license,
                               token=obj['data']['token'],
                               refresh_token=obj['data']['refreshToken'],
                               expires_in=obj['data']['expiresIn'],
                               timestamp=datetime.utcnow())
            db.session.add(my_token)
            db.session.commit()
        else:
            hz_token[0].token = obj['data']['token']
            hz_token[0].refresh_token = obj['data']['refreshToken']
            hz_token[0].expires_in = obj['data']['expiresIn']
            hz_token[0].timestamp = time_now
            print hz_token[0]
            db.session.add(hz_token[0])
            db.session.commit()
    else:
        print "error in function job_get_token() /////:", res
        print "url= ", url
        print "req data= ", test_data


def job_get_location():
    time_now = datetime.utcnow()
    hz_token = HzToken.query.all()
    # 还没有获取过token，或者token过期
    dt_time = (time_now - hz_token[0].timestamp).total_seconds()
    if len(hz_token) == 0 and dt_time > hz_token[0].expires_in:
        return

    url = "https://api.joysuch.com:46000/WebLocate/locateResults"
    data = {'accessToken': hz_token[0].token,
            'userIds': ["1918E00103AA"],
            'timePeriod': 5000}
    headers = {'Content-Type': 'application/json;charset=UTF-8'}
    req = urllib2.Request(url=url, data=json.dumps(data), headers=headers)
    res_data = urllib2.urlopen(req)
    res = res_data.read()
    obj = json.loads(res)
    if obj["errorCode"] == 0:
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
        print "error in function job_get_location(): ", res
        print "url= ", url
        print "req data= ", data

scheduler = BackgroundScheduler()
scheduler.add_job(job_get_token, 'interval', seconds=JOB_INTERVAL, id='my_job_get_token',
                  next_run_time=datetime.now())
scheduler.add_job(job_get_location, 'interval', seconds=3, id='my_job_get_location',
                  next_run_time=datetime.now())
scheduler.start()
