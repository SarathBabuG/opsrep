from django_apscheduler.jobstores import register_events, DjangoJobStore
from apscheduler.schedulers.background import BackgroundScheduler


schedObj = BackgroundScheduler()
schedObj.add_jobstore(DjangoJobStore(), 'default')

if schedObj:
    for _job in schedObj.get_jobs():
        schedObj.unschedule_job(_job)
    
''' Add all schedule jobs here '''
#schedObj.add_job(get_cn_agent_counts, 'interval', minutes=10)

print ("Starting scheduler")
register_events(schedObj)
schedObj.start()
print ("Started")