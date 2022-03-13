# Retic
from retic import App as app


BACKEND_WORDPRESS = {
    u"base_url": app.config.get('APP_BACKEND_WORDPRESS'),
    u"posts": "/posts",
    u"posts_type": "/posts-type",
}

BACKEND_IMAGES = {
    u"base_url": app.config.get('APP_BACKEND_IMAGES'),
    u"images_remote": "/images/remote",
}
BACKEND_ZIP = {
    u"base_url": app.config.get('APP_BACKEND_ZIP'),
    u"zip_images": "/zip-images",
}

APP_BACKEND = {
    u"wordpress": BACKEND_WORDPRESS,
    u"images": BACKEND_IMAGES,
    u"zip": BACKEND_ZIP,
}

"""Add Backend apps"""
app.use(APP_BACKEND, "backend")
