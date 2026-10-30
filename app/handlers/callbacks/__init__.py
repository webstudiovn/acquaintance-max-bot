__all__ = ("router",)

from maxo import Router

from .reaction_handler import router as reaction_handler_router
from .matches_handler import router as matches_handler_router
from .payment_handler import router as payment_handler_router
from .tariffs_handler import router as tariffs_handler_router

router = Router(name=__name__)

router.include(
    reaction_handler_router,
    matches_handler_router,
    payment_handler_router,
    tariffs_handler_router
  )