from maxo import Router
from .add_channel import router as add_router
from .publish_handler import router as publish_router

router = Router(name=__name__)
router.include(add_router,
               publish_router)
