'''
/*
 * This computer program is the confidential information and proprietary trade
 * secret  of  OpsRamp, Inc. Possessions and use of this program must conform
 * strictly to the license agreement between the user and OpsRamp, Inc., and
 * receipt or possession does not convey any rights to divulge, reproduce, or
 * allow others to use this program without specific written authorization of
 * OpsRamp, Inc.
 * 
 * Copyright (c) 2018 OpsRamp, Inc. All rights reserved. 
 */
'''
from django_apscheduler.jobstores import register_events, DjangoJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta
from dashboards.ops.manager import get_cn_agent_counts

schedObj = BackgroundScheduler({'daemon': True})
schedObj.add_jobstore(DjangoJobStore(), 'default')

if schedObj:
    for _job in schedObj.get_jobs():
        schedObj.unschedule_job(_job)
    
''' Add all schedule jobs here '''
ten_min_trigger = IntervalTrigger(minutes=15, start_date=datetime.now() + timedelta(seconds=15))
schedObj.add_job(get_cn_agent_counts, ten_min_trigger, max_instances=2, id='get_cn_agent_counts', replace_existing=True)
#schedObj.add_job(get_cn_agent_counts, "interval", minutes=10, next_run_time=(datetime.now() + timedelta(seconds=15)))

print ("Starting scheduler")
register_events(schedObj)
schedObj.start()
print ("Started")