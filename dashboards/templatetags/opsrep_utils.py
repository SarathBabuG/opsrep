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
from django import template
from decimal import Decimal
from django.http import QueryDict
from django.utils.encoding import force_str
from django.utils.functional import Promise
from django.utils.safestring import mark_safe

import json
import datetime

ISO_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'

register = template.Library()


@register.filter
def dict_lookup(the_dict, key):
    try:
        return the_dict[key]
    except KeyError:
        return ''


#@register.filter
#def jsonify(data):
#    return mark_safe(json.dumps(data))


@register.filter
def load_json(data):
    return json.loads(data)


@register.simple_tag
def active(request, pattern):
    import re
    if re.search(pattern, request.path):
        return 'active'
    return ''


"""
Ref: https://stackoverflow.com/questions/3345076/django-parse-json-in-my-template-using-javascript/3345111
Usage:
{% import json_tags %}
var = myJsObject = {{ template_var|to_json }};
Features:
- Built in support for dates, datetimes, lazy translations.
- Safe escaping of script tags.
- Support for including QuryDict objects.
- Support for custom serialization methods on objects via defining a `to_json()` method.
"""
def json_handler(obj):
    if callable(getattr(obj, 'to_json', None)):
        return obj.to_json()
    elif isinstance(obj, datetime.datetime):
        return obj.strftime(ISO_DATETIME_FORMAT)
    elif isinstance(obj, datetime.date):
        return obj.isoformat()
    elif isinstance(obj, datetime.time):
        return obj.strftime('%H:%M:%S')
    elif isinstance(obj, Decimal):
        return float(obj)  # warning, potential loss of precision
    elif isinstance(obj, Promise):
        return force_str(obj)  # to support ugettext_lazy
    else:
        return json.JSONEncoder().default(obj)


@register.filter
def to_json(obj):
    def escape_script_tags(unsafe_str):
        # seriously: http://stackoverflow.com/a/1068548/8207
        return unsafe_str.replace('</script>', '<" + "/script>')

    # json.dumps does not properly convert QueryDict array parameter to json
    if isinstance(obj, QueryDict):
        obj = dict(obj)
    return mark_safe(escape_script_tags(json.dumps(obj, default=json_handler)))
