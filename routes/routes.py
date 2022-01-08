# Retic
from retic import Router

# Controllers
import controllers.muysexy as muysexy

router = Router()

router.get("/images/latest", muysexy.get_latest)
router.get("/images/posts", muysexy.get_info_post)
