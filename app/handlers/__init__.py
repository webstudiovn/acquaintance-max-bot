__all__ = ("router",)

from maxo import Router

from .commands import router as commands_router
from .callbacks import router as callbacks_router
from .channels import router as channels_router

router = Router(name=__name__)

router.include(
    commands_router,
    callbacks_router,
    channels_router,
)