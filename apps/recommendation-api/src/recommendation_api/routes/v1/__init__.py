"""API v1 route modules."""

from recommendation_api.routes.v1.personalized import router as personalized_router
from recommendation_api.routes.v1.popular import router as popular_router
from recommendation_api.routes.v1.similar import router as similar_router
from recommendation_api.routes.v1.trending import router as trending_router

__all__ = [
    "trending_router",
    "popular_router",
    "personalized_router",
    "similar_router",
]
