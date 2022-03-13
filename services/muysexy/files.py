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

# services
from services.wordpress import wordpress
from services.muysexy.images import get_latest, get_info_post
from services.zip import zip

# Models
from models import Scrapper
import services.general.constants as constants


WEBSITE_POST_TYPE = app.config.get('WEBSITE_POST_TYPE')
URL_SENDFILES_WEB = app.config.get('URL_SENDFILES_WEB')
MUYSEXY_URL_API_BASE = app.config.get('MUYSEXY_URL_API_BASE')


def build_items_to_upload(
    items,
    headers,
    limit_publish,
):
    """Define all variables"""
    _items = []
    """For each novel do the following"""
    for _item in items:
        _headers = {
            **headers,
            # u'without_oauth_session': '1',
        }
        """Find novel in db"""
        _oldpost = wordpress.search_post_by_slug(
            _item['slug'], headers=_headers, post_type=WEBSITE_POST_TYPE
        )
        if _oldpost and 'meta' in _oldpost['data'] and 'files' in _oldpost['data']['meta'] and int(_oldpost['data']['meta']['files']):
            continue

        _publication = get_info_post(
            url="/{0}".format(_item['slug']),
        )
        """Check if it has any problem"""
        if not _publication['valid']:
            continue

        """Set data"""
        _data = {
            **_item,
            **_publication['data'],
            **_oldpost['data']
        }
        """Add novel to list"""
        _items.append(_data)
        """Check the limit"""
        if len(_items) >= limit_publish:
            break
    return _items


def build_post_content(item, description_upload, title, credential, content=""):
    _links_str = ""
    _upload = zip.zip_images(
        item['images'],
        description_upload,
        item['slug'],
        credential
    )
    _subtitle = "{0} MEGA".format(title)
    if _upload['valid'] is False:
        return None
    _links_str = """
        <p style="text-align: center;">
        <a href="{1}/#/downloads/{2}" target="_blank" rel="noopener noreferrer">
                <img class="alignnone size-full wp-image-5541" src="/wp-content/uploads/2022/03/packs-mega.png" alt="{0}" width="300" height="60" />
            </a>
        </p>
        """.format(
        _subtitle,
        URL_SENDFILES_WEB,
        _upload['data']['code']
    )
    if _links_str == "":
        return None
    _content_download = """
        <p style="text-align: center;">DESCARGA AQUI:</p>
        {0}
    """.format(
        _links_str,
    )
    _post_content = ""
    _split_text = "Únete y participa en nuestros"
    _content_parts = content.split(_split_text)
    if len(_content_parts) > 1:
        _post_content = _content_parts[0] + \
            _content_download + _split_text + ' '.join(_content_parts[1:])
    else:
        _post_content = content + _content_download

    return _post_content


def update_item_wp(
    items, headers,
    description_upload,
    credential
):
    """Publish all items but it check if the post exists,
    in this case, it will update the post.

    :param items: List of novel to will publish
    """
    """Define all variables"""
    _published_items = []
    """For each novels do to the following"""
    for _item in items:
        """Generate content"""
        _content = build_post_content(
            _item,
            description_upload,
            title=_item['title'],
            credential=credential,
            content=_item['post_content']
        )
        _data = {
            u'content': _content,
            u'meta': {
                **_item['meta'],
                'files': 1
            }
        }
        """Create the post"""
        _post = wordpress.update_post(
            post_id=_item['ID'],
            data=_data,
            headers=headers,
        )
        """Check if is a valid post"""
        if not _post or not _post['valid'] or not 'id' in _post['data']:
            """Add post to novel"""
            continue

        _published_items.append(_post['data'])
    """Return the posts list"""
    return _published_items


def upload_items(
    limit,
    headers,
    limit_publish,
    page,
    description_upload,
    credential,
):
    _items = get_latest(
        limit=limit,
        page=page,
    )

    if _items['valid'] is False:
        return []
    _builded_items = build_items_to_upload(
        _items['data'],
        headers,
        limit_publish,
    )

    if not _builded_items:
        return []

    """Publish or update on website"""
    _created_posts = update_item_wp(
        _builded_items,
        headers=headers,
        description_upload=description_upload,
        credential=credential
    )
    return _created_posts


def add_files_post(
    limit,
    headers,
    limit_publish,
    description_upload,
    page=1,
    credential=None,
):
    _created_posts = upload_items(
        limit,
        headers,
        limit_publish,
        page=page,
        description_upload=description_upload,
        credential=credential,
    )
    print("*********len(_created_posts)*********:" + str(len(_created_posts)))
    """Check if almost one item was published"""
    if(len(_created_posts) == 0):
        """Find in database"""
        _session = app.apps.get("db_sqlalchemy")()
        _item = _session.query(Scrapper).\
            filter(Scrapper.key == MUYSEXY_URL_API_BASE, Scrapper.type == constants.TYPES['images']).\
            first()

        print("*********if _item is None*********")
        if _item is None:
            print("*********_item = Scrapper*********")
            _item = Scrapper(
                key=MUYSEXY_URL_API_BASE,
                type=constants.TYPES['images'],
                value=page+1
            )
            """Save chapters in database"""
            _session.add(_item)
            _session.flush()
            """Save in database"""

        _created_posts = upload_items(
            limit,
            headers,
            limit_publish,
            page=_item.value,
            description_upload=description_upload,
            credential=credential,
        )

        if(len(_created_posts) == 0):
            print("*********_item.value = *********")
            _item.value = str(int(_item.value)+1)

        _session.commit()
        _session.close()

    _data_respose = {
        u"items":  _created_posts
    }
    return success_response(
        data=_data_respose
    )
