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
#from dashboards.models import Stats
#from dashboards.ops.utils import http_request
from dashboards.ops import properties
from dashboards.ops.connection import DBCmd, executeQuery, SQL
from datetime import date
from dashboards.models import Period, Source, ProductStats, MonthlyStats

def get_product_stats_data():
    sources = properties.source_maps[properties.product]
    stats_interval = "30"

    _hash = {'partners': {}, 'tenants': {}, 'users': {}}
    for source in sources:
        query1 = "select class_code,activated,count(*) as cnt from organizations where source=%s and class_code in ('msp','client') group by class_code, activated;"
        results1  = executeQuery( DBCmd(SQL, query1, [source]) )[1]
        for result in results1:
            _key = result[0]
            if result[0] == 'msp':
                _key = "partners"
            elif result[0] == 'client':
                _key = "tenants"

            try:
                _hash[_key][result[1]] += result[2]
            except:
                _hash[_key][result[1]] = result[2]

        query2 = "select activated,count(*) as au from users where source=%s group by activated;"
        results2  = executeQuery( DBCmd(SQL, query2, [source]) )[1]
        for result in results2:
            try:
                _hash['users'][result[0]] += result[1]
            except:
                _hash['users'][result[0]] = result[1]

    org_analytics = _hash

    query3    = "select count(*) as dev from device_data where state in ('inactive','deleted', 'discovered');"
    results3  = executeQuery( DBCmd(SQL, query3) )[1]
    query4    = "select count(*) as dev from device_data;"
    results4  = executeQuery( DBCmd(SQL, query4) )[1]
    
    inactive  = results3[0][0]
    active    = results4[0][0] - inactive
    org_analytics['resources'] = {
        0: inactive,
        1: active
    }
    
    query5 = "select count(*) from device_data where state='active' and created_date > DATE_SUB(now(), interval %s day);" % (stats_interval)
    results5 = executeQuery( DBCmd(SQL, query5) )[1]
    managed_resources  = results5[0][0]

    query6 = "select count(*) as alertscount from alerts.alert_master where ts > UNIX_TIMESTAMP(DATE_SUB(now(), interval %s day))*1000;" % (stats_interval)
    results6 = executeQuery( DBCmd(SQL, query6) )[1]
    alerts_created = results6[0][0]
    
    query7 = "select count(*) from sd_ticket where created_date > DATE_SUB(now(), interval %s day);" % (stats_interval)
    results7 = executeQuery( DBCmd(SQL, query7) )[1]
    tickets_created = results7[0][0]
    
    query8 = "select count(*) from schedule_reports where created_time > DATE_SUB(now(), interval %s day);" % (stats_interval)
    results8 = executeQuery( DBCmd(SQL, query8) )[1]
    reports_created = results8[0][0]
    
    query9 = "select count(*) from dsb_dashboards where created_time > DATE_SUB(now(), interval %s day);" % (stats_interval)
    results9 = executeQuery( DBCmd(SQL, query9) )[1]
    dashboards_created = results9[0][0]
    
    query10 = "select count(*) from video_session where start_date > DATE_SUB(now(), interval %s day);" % (stats_interval)
    results10 = executeQuery( DBCmd(SQL, query10) )[1]
    recordings_created = results10[0][0]

    query11 = "select org_class_code,count(DISTINCT(login_name)) from login_history where login_time > DATE_SUB(now(), interval %s day) group by org_class_code;" % (stats_interval)
    results11 = executeQuery( DBCmd(SQL, query11) )[1]
    user_sessions = {}
    for result in results11:
        user_sessions[result[0]] = result[1]
    
    query12 = "select count(*) from login_history where login_time > DATE_SUB(now(),interval %s day);" % (stats_interval)
    results12 = executeQuery( DBCmd(SQL, query12) )[1]
    total_user_sessions = results12[0][0]

    org_analytics['stats'] = {
        'resources_added'    : managed_resources,
        'alerts_created'     : alerts_created,
        'tickets_created'    : tickets_created,
        'reports_created'    : reports_created,
        'dashboards_created' : dashboards_created,
        'recordings_created' : recordings_created,
        'logged_in_users'    : {
            'total_user_sessions'   : total_user_sessions,
            'partner_user_sessions' : user_sessions['msp'],
            'client_user_sessions'  : user_sessions['client'],
            'sp_user_sessions'      : user_sessions['service_provider']
        }
    }

    c_month = date.today().month
    c_year  = date.today().year
    periodObj = Period.objects.get_or_create(year=c_year, month=c_month)[0]
    for src in list(dict(Source.choices).keys()):
        sourceObj = Source.objects.get_or_create(name=src)[0]
        ProductStats(period=periodObj, source=sourceObj, active=org_analytics[src][1], inactive=org_analytics[src][0]).save()
        #ProductStats.objects.get_or_create(period=periodObj, source=sourceObj, active=org_analytics[src][1], inactive=org_analytics[src][0])

    for src in org_analytics['stats'].keys():
        if src != 'logged_in_users':
            MonthlyStats(period=periodObj, attrname=src, attrvalue=org_analytics['stats'][src]).save()
            #MonthlyStats.objects.get_or_create(period=periodObj, attrname=src, attrvalue=org_analytics['stats'][src])
        else:
            for _key in org_analytics['stats'][src].keys():
                MonthlyStats(period=periodObj, attrname=_key, attrvalue=org_analytics['stats'][src][_key]).save()
                #MonthlyStats.objects.get_or_create(period=periodObj, attrname=_key, attrvalue=org_analytics['stats'][src][_key])

    properties.orgstats = org_analytics