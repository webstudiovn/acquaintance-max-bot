__all__ = ("router",)

from maxo import Router

from .base_commands import router as base_commands_router
from .profile import router as profile_updated_router
from .search_pairs import router as search_pairs_router
from .my_profile import router as my_profile_router

router = Router(name=__name__)

router.include(
    base_commands_router,
    profile_updated_router,
    search_pairs_router,
    my_profile_router
)