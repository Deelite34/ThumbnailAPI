from datetime import datetime, timedelta

from django.shortcuts import render
from django.views import View
from pytz import timezone

from API.models import Image


class DisplayImageView(View):
    def get(self, request, slug):
        """
        Checks if image is expired, and displays image if not
        :param request:
        :param slug: string identifying specific image to display
        """

        image = Image.objects.get(slug=slug)
        context = {"image_path": image.image.url, "expired": image.is_expired}
        return render(request, "img/image.html", context=context)
