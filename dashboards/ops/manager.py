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
from datetime import date, datetime
import json, calendar

from dashboards.models import ProductStats
from dashboards.models import MonthlyStats
from dashboards.ops.utils import http_request
#from dashboards.ops.jobs import schedObj
from dashboards.ops import properties

from dashboards.ops.connection import DBCmd, executeQuery, SQL

colors_codes = {
    'green'       : '#008000',
    'olive'       : '#6B8E23',
    'limegreen'   : '#32CD32',
    'yellowgreen' : '#9ACD32',

    'red'         : '#D55454',
    'crimson'     : '#DC143C',
    'salmon'      : '#FA8072',
    'indianred'   : '#CD5C5C',
    'lightcoral'  : '#F08080',
    'tomato'      : '#FF6347',
    
    'blue'          : '#36A2EB',
    'navy'          : '#000080',
    'royalblue'     : '#4169E1',
    'slateblue'     : '#6A5ACD',
    'darkslateblue' : '#483D8B',
    'steelblue'     : '#4682B4',
    'cornflowerblue': '#6495ED',
    
    'yellow'      : '#FFCE56'

}


def pod_rsrc_stats_doughnut(month=date.today().month, year=date.today().year):
    chart_type = "doughnut"
    datasets   = []
    labels     = ['Active', 'Inactive']
    options    = {
        "responsive" : True,
        "title": {
            "display": True,
            "position": 'left',
        },
        "legend": {
            "position": 'bottom',
            "labels": {"boxWidth": 20}
        }
    }
    options.update({
        "pieceLabel" : {
            "render"    : "value",
            "position"  : "default",
            "fontSize"  : 9,
            "fontColor" : "#fff",
            "fontStyle" : "bold",
            "fontFamily": "'Helvetica Neue', 'Helvetica', 'Arial', 'sans-serif'"
        }
    })

    colors   = [colors_codes['olive'], colors_codes['red']]
    itom_stats = ProductStats.objects.filter(period__year=year, period__month=month)

    product_hash = {}
    for _stat in itom_stats:
        src = _stat.source.name
        product_hash[src] = {'active': _stat.active, 'inactive': _stat.inactive}

        dashboard = src.upper()
        datasets.append({
            'name': dashboard,
            'dataset': {
                'label': dashboard,
                'data': [_stat.active, _stat.inactive],
                'backgroundColor': colors,
                'hoverBackgroundColor': colors
            }
        })
 
    context = {'chart_type': chart_type, 'options': str(json.dumps(options)), 'labels': str(json.dumps(labels)), 'data_sets': str(json.dumps(datasets))}
    return context



def pod_rsrc_stats_pie():
    last = 6

    months = dict((k, v) for k,v in enumerate(calendar.month_abbr))
    del months[0]
    
    month = date.today().month
    year  = date.today().year

    sources    = ['partners', 'tenants', 'users', 'resources']
    chart_type = "bar"
    datasets   = []
    options    = {
        "responsive" : True,
        "legend": {
            "position": 'bottom',
            "labels": {"boxWidth": 20}
        }
    }

    itom_stats = ProductStats.objects.filter(period__year=year, period__month__gt=(month-last), period__month__lt=(month+1)).order_by('period__month')
    if month < last:
        prev_year   = year - 1
        prev_months = last - (month % last)
        py_itom_stats = ProductStats.objects.filter(period__year=prev_year, period__month__gt=(12-prev_months), period__month__lt=(12+1)).order_by('period__month')
        cy_itom_stats = ProductStats.objects.filter(period__year=year, period__month__gt=(month-(month % last)), period__month__lt=(month+1)).order_by('period__month')
        itom_stats = (list(py_itom_stats) + list(cy_itom_stats))

    product_hash = {}
    labels = []
    for _stat in itom_stats:
        if months[_stat.period.month] not in labels:
            labels.append(months[_stat.period.month])

        if _stat.source.name not in product_hash:
            product_hash[_stat.source.name] = {'active': [], 'inactive': []}

        product_hash[_stat.source.name]['active'].append(_stat.active)
        product_hash[_stat.source.name]['inactive'].append(_stat.inactive)

    """
    Result:
    _hash = {
        "msp": {
            "active": [12, 13, 10],      #10th, 11th, 12th months values
            "inactive": [12, 13, 10],
        },
        "tenants": {
            "active":   [11, 7, 6],      #10th, 11th, 12th months values
            "inactive": [8, 31, 10],
        },
        
    }
    """

    for src in sources:
        if src not in product_hash:
            continue

        dashboard       = src.upper()
        active_values   = product_hash[src]['active']
        inactive_values = product_hash[src]['inactive']
        datasets.append({
            'name'     : dashboard,
            'dataset'  : [{
                'label': 'Active',
                'data' : active_values,
                'backgroundColor' : colors_codes['olive'],
                'borderColor' : colors_codes['olive'],
                'highlightFill' : 'rgba(151,187,205,0.75)',
                'highlightStroke' : 'rgba(151,187,220,1)',
            },{
                'label': 'Inactive',
                'data' : inactive_values,
                'backgroundColor' : colors_codes['red'],
                'borderColor' : colors_codes['red'],
                'highlightFill' : 'rgba(151,187,205,0.75)',
                'highlightStroke' : 'rgba(151,187,205,1)',
            }]

        })

    context = {'chart_type': chart_type, 'options': json.dumps(options), 'labels': json.dumps(labels), 'data_sets': json.dumps(datasets)}
    return context


#@schedObj.scheduled_job("interval", minutes=15, id="get_cn_agent_counts", next_run_time=(datetime.now() + timedelta(seconds=15)))
def get_cn_agent_counts():
    cn_hosts = properties.configs[properties.saas_key]["csnodes"]
    
    sessions_url = "https://%s:8443/stats"
    sessions = {}
    csplit = str.split

    for cn in cn_hosts:
        try:
            cn_url = sessions_url % (cn)
            response = http_request(cn_url).decode().split("<br>")
            sessions[cn.split(".")[0]] = dict([(x[0], x[-1]) for x in map(csplit, response)])
        except:
            sessions[cn.split(".")[0]] = {"Total": 0, "Agent": 0, "Gateway": 0}

    properties.statsObj = {"1arc": sessions, "time": str(datetime.now())}



def get_monthly_usage_stats(month=date.today().month, year=date.today().year):

    last = 6

    months = dict((k, v) for k,v in enumerate(calendar.month_abbr))
    del months[0]

    #sources    = ['partners', 'tenants', 'users', 'resources']    
    sources    = ['resources_added','alerts_created','tickets_created','reports_created','dashboards_created','recordings_created']
    datasets   = []

    itom_stats = MonthlyStats.objects.filter(period__year=year, period__month__gt=(month-last), period__month__lt=(month+1)).order_by('period__month')
    if month < last:
        prev_year   = year - 1
        prev_months = last - (month % last)
        py_itom_stats = MonthlyStats.objects.filter(period__year=prev_year, period__month__gt=(12-prev_months), period__month__lt=(12+1)).order_by('period__month')
        cy_itom_stats = MonthlyStats.objects.filter(period__year=year, period__month__gt=(month-(month % last)), period__month__lt=(month+1)).order_by('period__month')
        itom_stats = (list(py_itom_stats) + list(cy_itom_stats))

    product_hash = {}
    labels = []
    
    for _stat in itom_stats:
        if months[_stat.period.month] not in labels:
            labels.append(months[_stat.period.month])

        if _stat.attrname not in product_hash:
            product_hash[_stat.attrname] = {'active': []}

        product_hash[_stat.attrname]['active'].append(_stat.attrvalue)


    for src in sources:
        if src not in product_hash:
            continue

        active_values   = product_hash[src]['active']
        datasets.append(active_values)



    # For monthly logic stats        
    usage_stats = MonthlyStats.objects.filter(period__year=year, period__month=month)
    user_stats = ProductStats.objects.filter(period__year=year, period__month=month)
    _hash = {}
    for _stat in usage_stats:
        _hash[_stat.attrname] = _stat.attrvalue

    user_hash = {}
    for _stat in user_stats:
        if _stat.source.name == "resources":
            user_hash['active'] = _stat.active
            user_hash['inactive'] = _stat.inactive

    context = {'resources_stats': str(json.dumps(user_hash)), 'usage_stats': str(json.dumps(_hash)), 'labels': str(json.dumps(labels)) ,
            'datasets': json.dumps(datasets)}
    return context


def get_elasticsearch_cluster_info():
    es_configs = properties.configs[properties.saas_key]["csnodes"]
    EURL = "http://%s:%s" % (es_configs['nodes'][0], es_configs['port'])

    health_data    = json.loads(http_request(EURL + es_configs['health_uri']).decode())    
    stats_data     = json.loads(http_request(EURL + es_configs['stats_uri']).decode())
    cluster_health = {
        'cluster.name'          : health_data['cluster_name'],
        'cluster.state'         : health_data['status'],
        'cluster.nodes'         : health_data['number_of_nodes'],
        'cluster.nodes.data'    : health_data['number_of_data_nodes'],
        'active.primary.shards' : health_data['active_primary_shards'],
        'active.shards'         : health_data['active_shards'],
        'primaries.docs' : stats_data['_all']['primaries']['docs']['count'],
        'primaries.size' : stats_data['_all']['primaries']['store']['size_in_bytes'],
        'indices'        : []
    }


    indices_data = http_request(EURL + es_configs['indices_uri']).decode()
    for index_line in indices_data.splitlines():
        index_stats = index_line.split()
        _index = index_stats[2]
        _hash = {
            _index: {
                'index.health'           : index_stats[0],
                'index.state'            : index_stats[1],
                'number_of_shards'       : index_stats[4],
                'number_of_replicas'     : index_stats[5],
                'primaries.docs.count'   : index_stats[6],
                'primaries.docs.deleted' : index_stats[7],
                'total.size'             : index_stats[8],
                'primaries.size'         : index_stats[9]
            }
        }
        cluster_health['indices'].append(_hash)


    indices = cluster_health["indices"]
    indices_list = []
    for i in indices:
        for key, value in i.items():
            value_dict = dict()
            value_dict.update({
                'name': key,
                'health': value['index.health'],
                'shards': value['number_of_shards'],
                'replicas': value['number_of_replicas'],
                'docs_count': value['primaries.docs.count'],
                'docs_deleted': value['primaries.docs.deleted'],
                'primaries_size': value['primaries.size'],
                'total_size': value['total.size']
            })
            indices_list.append(value_dict)

    context = {'es_stats': str(json.dumps(cluster_health)), 'indices': str(json.dumps(indices)),'indices_list': str(json.dumps(indices_list))}
    return context
