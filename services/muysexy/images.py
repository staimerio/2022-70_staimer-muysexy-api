"""Services for novels controller"""

# Retic
from retic import env, App as app

# Requests
import requests

# Time
from time import sleep

# bs4
from bs4 import BeautifulSoup

# Services
from retic.services.responses import success_response, error_response
from services.utils.general import get_node_item, get_https_url
from retic.services.general.urls import slugify

# Models

# Constants


class MuySexy(object):

    def __init__(self):
        """Set the variables"""
        self.url_base = app.config.get("MUYSEXY_URL_API_BASE")
        self.site = app.config.get("MUYSEXY_SITE")
        self.host = app.config.get("MUYSEXY_HOST")

    def get_post_info(self, url):
        r_download_page = requests.get("{0}{1}".format(self.url_base, url))
        _soup = BeautifulSoup(r_download_page.content, 'html.parser')
        """Get info about the item"""
        _info = self.get_data_post(_soup)
        if not _info:
            """Return error if data is invalid"""
            return error_response(
                msg="Item not found."
            )
        """Set the data response"""
        _data_response = {
            **_info
        }
        return success_response(
            data=_data_response
        )

    def get_data_post(self, page):
        _images = []
        _post = page.find(id="mvp-content-main")
        _images_raw = _post.find_all("img", src=True)
        _cover = ""
        for _image_raw in _images_raw:
            _url = _image_raw.attrs['data-lazy-src'] if 'data-lazy-src' in _image_raw.attrs else _image_raw['src']
            if "grupo" in _url or "mega" in _url:
                continue
            _images.append(_url)
            if ".gif" not in _url and ".webp" not in _url:
                _cover = _url

        _title = page.find("h1").text

        _genres_box = page.find(class_="mvp-post-tags")

        _genres = [_genre.text.strip()
                   for _genre in _genres_box.find_all("a", href=True)]
        _categories = ['Only Fans']
        return {
            'title': _title,
            'cover': _cover,
            'genres': _genres,
            "images": _images,
            'categories': _categories,
        }


def get_instance():
    """Get an MTLNovel instance from a language"""
    return MuySexy()


def get_data_items_raw(instance, page=0):
    """GET Request to url"""
    _url = "{0}/fotos/page/{1}".format(instance.url_base, page)
    _req = requests.get(_url)
    """Format the response"""
    _soup = BeautifulSoup(_req.content, 'html.parser')
    _items = []
    for _posts in _soup.find_all(class_='infinite-post'):
        _items.append(_posts.find(class_='mvp-main-blog-text').find('a'))
    return _items


def get_data_item_json(instance, item):
    try:
        """Get url"""
        _url = item['href'].replace(instance.url_base, '')
        """Check that the url exists"""
        _title = item.text.strip()
        return get_node_item(_url, _title, instance.host, instance.site)
    except Exception as e:
        return None


def get_list_json_items(instance, page, limit=100):
    """Declare all variables"""
    _items = list()
    """Get article html from his website"""
    _items_raw = get_data_items_raw(instance, page)
    for _item_raw in _items_raw:
        _item_data = get_data_item_json(instance, _item_raw)
        """Check if item exists"""
        if not _item_data:
            continue
        """Slugify the item's title"""
        _item_data['slug'] = slugify(_item_data['title'])
        """Add item"""
        _items.append(_item_data)
        """Validate if has the max"""
        if len(_items) >= limit:
            break
    """Return items"""
    return _items


def get_latest(limit=10, page=1):
    """Settings environment"""
    instance = get_instance()
    """Request to hitomi web site for latest novel"""
    _items_raw = get_list_json_items(
        instance, page, limit)
    """Validate if data exists"""
    if not _items_raw:
        """Return error if data is invalid"""
        return error_response(
            msg="Files not found."
        )
    """Response data"""
    return success_response(
        data=_items_raw
    )


def get_info_post(url):
    """Settings environment"""
    instance = get_instance()
    """Request to hitomi web site for latest novel"""
    _result = instance.get_post_info(url)
    """Validate if data exists"""
    if not _result['valid']:
        """Return error if data is invalid"""
        return error_response(
            msg="Files not found."
        )
    """Response data"""
    return _result
