# Retic
from retic import Router

# Controllers
import controllers.muysexy as muysexy
import controllers.files as files

router = Router()

router.get("/images/latest", muysexy.get_latest)
router.get("/images/posts", muysexy.get_info_post)

router.post("/files/posts", files.add_files_post)
