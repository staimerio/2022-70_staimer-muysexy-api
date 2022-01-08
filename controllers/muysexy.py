# Retic
from retic import Request, Response, Next, App as app

# Services
from retic.services.responses import success_response, error_response
from retic.services.validations import validate_obligate_fields
from services.muysexy import images

MUYSEXY_LIMIT_LATEST = app.config.get('MUYSEXY_LIMIT_LATEST')
MUYSEXY_PAGES_LATEST = app.config.get('MUYSEXY_PAGES_LATEST')



def get_latest(req: Request, res: Response, next: Next):
    """Get all novel from latests page"""
    items = images.get_latest(
        limit=req.param('limit', MUYSEXY_LIMIT_LATEST, int),
        page=req.param('page', MUYSEXY_PAGES_LATEST, int),
    )
    """Check if exist an error"""
    if items['valid'] is False:
        return res.bad_request(items)
    """Transform the data response"""
    _data_response = {
        u"items": items.get('data')
    }
    """Response the data to client"""
    res.ok(success_response(_data_response))

def get_info_post(req: Request, res: Response, next: Next):
    """Validate obligate params"""
    _validate = validate_obligate_fields({
        u'url': req.param('url'),
    })
    
    """Check if has errors return a error response"""
    if _validate["valid"] is False:
        return res.bad_request(
            error_response(
                "{} is necesary.".format(_validate["error"])
            )
        )
    """Get all novel from latests page"""
    _result = images.get_info_post(
        url=req.param('url'),
    )
    """Check if exist an error"""
    if _result['valid'] is False:
        return res.bad_request(_result)
    """Transform the data response"""
    _data_response = {
        **_result.get('data')
    }
    """Response the data to client"""
    res.ok(success_response(_data_response))