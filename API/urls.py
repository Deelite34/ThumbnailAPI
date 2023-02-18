from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter

from .views import ImageUploadView, TimeLimitedThumbnailView

router = DefaultRouter()
router.register("all", ImageUploadView, basename="all")
router.register("timed", TimeLimitedThumbnailView, basename="timed")

api_v1 = "v1"

urlpatterns = [
    path(f"{api_v1}/thumbnails/", include(router.urls), name="thumbnail"),
    path(f"{api_v1}/auth/", include("djoser.urls.authtoken")),
    path(f"{api_v1}/auth/", include("djoser.urls.jwt")),
    path(f"{api_v1}/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        f"{api_v1}/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]
