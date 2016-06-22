from django.conf import settings
from django import template

import re

register = template.Library()

FC_URL_RE = re.compile('^' + settings.FCREPO['uri'] + 'rest/(.*)$')


@register.filter(name="link_if_fc")
def link_if_fc(url):
    m = FC_URL_RE.search(url)
    if m:
        fclink = '/repo/fc/' + m.group(1)
        return fclink
    else:
        return url
