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
from datetime import date, datetime, timedelta
import json, calendar

from dashboards.models import Stats
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
    products = ['ITOM', 'IMONSITE']
    for product in products:
        itom_stats = Stats.objects.filter(period__year=year, period__month=month, product__name=product)
    
        product_hash = {}
        for _stat in itom_stats:
            src = _stat.source.name
            product_hash[src] = {'active': _stat.active, 'inactive': _stat.inactive}

            dashboard = product + ' - ' + src
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
    last = 3

    months = dict((k, v) for k,v in enumerate(calendar.month_abbr))
    del months[0]
    
    month = date.today().month
    year  = date.today().year

    sources    = ['msp', 'tenants', 'users']
    chart_type = "bar"
    datasets   = []
    options    = {
        "responsive" : True,
        "legend": {
            "position": 'bottom',
            "labels": {"boxWidth": 20}
        }
    }
    
    products = ['ITOM', 'IMONSITE']
    for product in products:
        
        itom_stats = Stats.objects.filter(period__year=year, period__month__gt=(month-last), period__month__lt=(month+1), product__name=product).order_by('period__month')
        if month < last:
            prev_year   = year - 1
            prev_months = last - (month % last)
            py_itom_stats = Stats.objects.filter(period__year=prev_year, period__month__gt=(12-prev_months), period__month__lt=(12+1), product__name=product).order_by('period__month')
            cy_itom_stats = Stats.objects.filter(period__year=year, period__month__gt=(month-(month % last)), period__month__lt=(month+1), product__name=product).order_by('period__month')
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

            dashboard       = product + ' - ' + src
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
    pod1_rc_cns = properties.configs[properties.saas_key]["csnodes"] 
    
    sessions_url = "https://%s:8443/stats"
    sessions = {}
    csplit = str.split

    for cn in pod1_rc_cns:
        cn_url = sessions_url % (cn)
        print(cn_url)
        response = http_request(cn_url).decode().split("<br>")
        sessions[cn.split(".")[0]] = dict([(x[0], x[-1]) for x in map(csplit, response)])

    properties.statsObj = {"1arc": sessions, "time": str(datetime.now())}
