from django import template
import json

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
