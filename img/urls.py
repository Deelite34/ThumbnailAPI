from django.conf.urls.static import static
from django.urls import path
from django.views.decorators.cache import cache_page

from ThumbnailAPI import settings
from img.views import DisplayImageView

urlpatterns = [
    path("i/<str:slug>/",  cache_page(60*10)(DisplayImageView.as_view()), name="display_image"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
