"""Services for general utils"""

# Services
from retic.services.general.urls import slugify


def get_node_item(url, title, host, site=''):
    """Set item structure"""
    _item = {
        u'url': url,
        u'title': title,
        u'service': host,
        u'site': site
    }
    return _item

def outmarks(s):
    s = s.replace('\n', '')
    s = s.replace('\r', '')
    s = s.replace('\"', '\'')
    return s

def get_https_url(url):
    return url.replace('//','https://')