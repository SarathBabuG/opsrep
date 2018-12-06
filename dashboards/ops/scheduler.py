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
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
from dashboards.ops.jobs import get_cn_agent_counts
from dashboards.ops.jobs import get_product_stats_data
from dashboards.ops.jobs import get_pingdom_status

schedObj = BackgroundScheduler({'daemon': True})
schedObj.add_jobstore(DjangoJobStore(), 'default')

if schedObj:
    for _job in schedObj.get_jobs():
        schedObj.unschedule_job(_job)

''' Add all schedule jobs here '''
ten_min_trigger = IntervalTrigger(minutes=15, start_date=datetime.now() + timedelta(seconds=15))
schedObj.add_job(get_cn_agent_counts, ten_min_trigger, max_instances=1, id='get_cn_agent_counts', replace_existing=True)
#schedObj.add_job(get_cn_agent_counts, "interval", minutes=10, next_run_time=(datetime.now() + timedelta(seconds=15)))

hourly_trigger = IntervalTrigger(hours=1, start_date=datetime.now() + timedelta(seconds=15))
schedObj.add_job(get_pingdom_status, hourly_trigger, max_instances=1, id='get_pingdom_status', replace_existing=True)

monthly_trigger = CronTrigger(day=1, hour=0, minute=0, start_date=datetime.now() + timedelta(seconds=15))
#schedObj.add_job(get_product_stats_data, monthly_trigger, max_instances=1, id='get_product_stats_data', replace_existing=True)

print ("Starting scheduler")
register_events(schedObj)
schedObj.start()
print ("Started")