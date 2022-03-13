# Retic
from retic import Request, Response, Next, App as app

# Services
from retic.services.responses import success_response, error_response
from retic.services.validations import validate_obligate_fields
from services.muysexy import files

WEBSITE_LIMIT_LATEST = app.config.get('MUYSEXY_LIMIT_LATEST')
WEBSITE_PAGES_LATEST = app.config.get('MUYSEXY_PAGES_LATEST')
DESCRIPTION_UPLOAD = app.config.get('DESCRIPTION_UPLOAD')
STORAGE_CREDENTIALS_DEFAULT = app.config.get('STORAGE_CREDENTIALS_DEFAULT')



def add_files_post(req: Request, res: Response, next: Next):
    _headers = {}

    """Validate obligate params"""
    _validate = validate_obligate_fields({
        u'wp_login': req.param('wp_login'),
        u'wp_admin': req.param('wp_admin'),
        u'wp_username': req.param('wp_username'),
        u'wp_password': req.param('wp_password'),
        u'wp_url': req.param('wp_url'),
    })

    """Check if has errors return a error response"""
    if _validate["valid"] is False:
        return res.bad_request(
            error_response(
                "The param {} is necesary.".format(_validate["error"])
            )
        )

    # """Validate obligate params"""
    _headers = {
        u'oauth_consumer_key': req.headers.get('oauth_consumer_key') or app.config.get('WP_OAUTH_CONSUMER_KEY'),
        u'oauth_consumer_secret': req.headers.get('oauth_consumer_secret') or app.config.get('WP_OAUTH_CONSUMER_SECRET'),
        u'oauth_token': req.headers.get('oauth_token') or app.config.get('WP_OAUTH_TOKEN'),
        u'oauth_token_secret': req.headers.get('oauth_token_secret') or app.config.get('WP_OAUTH_TOKEN_SECRET'),
        u'base_url': req.headers.get('base_url') or app.config.get('WP_BASE_URL'),
    }

    wp_login=req.param('wp_login')
    wp_admin=req.param('wp_admin')
    wp_username=req.param('wp_username')
    wp_password=req.param('wp_password')
    wp_url=req.param('wp_url')

    limit_publish=req.param(
        'limit_publish', app.config.get('WEBSITE_LIMIT_PUBLISH'),  callback=int)
    
    """Publish items"""
    result = files.add_files_post(
        req.param('limit', WEBSITE_LIMIT_LATEST,  callback=int),
        headers=_headers,
        limit_publish=limit_publish,
        description_upload=req.param('description_upload', DESCRIPTION_UPLOAD),
        page=req.param('page', WEBSITE_PAGES_LATEST, callback=int),
        credential=req.headers.get('credential', STORAGE_CREDENTIALS_DEFAULT),
    )
    """Check if exist an error"""
    if result['valid'] is False:
        return res.bad_request(result)    
    # """Response the data to client"""
    res.ok(result)