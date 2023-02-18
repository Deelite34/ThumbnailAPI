import debug_toolbar
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from ThumbnailAPI import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("API.urls")),
    path("", include("img.urls"), name="root"),
    path("__debug__/", include(debug_toolbar.urls)),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
