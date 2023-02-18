import os
from datetime import datetime, timedelta

from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.http import HttpRequest
from easy_thumbnails.files import get_thumbnailer
from pytz import timezone
from rest_framework.request import Request

from ImageUploadAPI.settings import TIME_ZONE

from .custom_validators import (
    MaxValueValidatorIgnoreNull,
    MinValueValidatorIgnoreNull,
    validate_image_type,
)
from .utils import set_image_model_slug, user_directory_path


class AccountTier(models.Model):
    tier_name = models.CharField(max_length=50)
    allowed_thumbnail_sizes = ArrayField(models.PositiveIntegerField())

    can_create_original_img_link = models.BooleanField(default=False)
    can_create_time_limited_link = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.tier_name}"


class APIUser(AbstractUser):
    account_type = models.ForeignKey(
        AccountTier, null=True, blank=True, on_delete=models.SET_NULL
    )

    def __str__(self):
        return f"{self.username}"


class Image(models.Model):
    owner = models.ForeignKey(APIUser, on_delete=models.CASCADE)
    thumbnail_size = models.PositiveIntegerField(
        blank=True, null=True
    )  # blank for original imgs
    image = models.ImageField(
        upload_to=user_directory_path,
        validators=[validate_image_type],
    )
    slug = models.SlugField(max_length=15, blank=True)
    expire_time = models.IntegerField(
        default=None,
        blank=True,
        null=True,
        validators=[
            MinValueValidatorIgnoreNull(300),
            MaxValueValidatorIgnoreNull(30000),
        ],
    )
    created = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{os.path.basename(self.image.url)}"

    def save(self, *args, **kwargs):
        set_image_model_slug(self)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        tz = timezone(TIME_ZONE)
        date_now = tz.localize(datetime.now())
        date_created = self.created

        if not self.expire_time:
            return False
        if date_now > date_created + timedelta(seconds=self.expire_time):
            return True
        return False

    def get_url(self, request: HttpRequest):
        return request.get_host() + "/i/" + self.slug + "/"

    def make_thumbnails(self, owner: APIUser, request: Request) -> dict:
        """
        Bulk creates thumbnails for specified original image and its owner.
        If users tier can't grab original images, will delete original image after making thumbnails
        owner - APIUser model instance, that submited the image for thumbnail creation
        request - request object from DRF view
        """
        possible_thumbnail_sizes = owner.account_type.allowed_thumbnail_sizes

        thumbnails_to_be_bulk_created = []
        response_thumbnails = {"thumbnails": {}}

        for index, size in enumerate(possible_thumbnail_sizes):
            options = {"size": (size, size), "upscale": True, "crop": True}
            thumbnail = get_thumbnailer(self.image).get_thumbnail(options)
            thumbnails_to_be_bulk_created.append(
                Image(
                    owner=owner,
                    thumbnail_size=size,
                    image=str(thumbnail),
                )
            )

            current_image = thumbnails_to_be_bulk_created[index]
            set_image_model_slug(current_image)
            response_thumbnails["thumbnails"][
                current_image.thumbnail_size
            ] = current_image.get_url(request)

        if not owner.account_type.can_create_original_img_link:
            self.delete()
        else:
            response_thumbnails["thumbnails"][
                f"{self.image.width}x{self.image.height}"
            ] = self.get_url(request)

        Image.objects.bulk_create(thumbnails_to_be_bulk_created)
        return response_thumbnails

    def make_time_limited_thumbnail(
        self, owner: APIUser, request: Request, expire_time: int, size: int
    ) -> dict:
        options = {"size": (size, size), "upscale": True, "crop": True}
        thumbnail = get_thumbnailer(self.image).get_thumbnail(options)

        time_limited_img = Image.objects.create(
            owner=owner,
            thumbnail_size=size,
            image=str(thumbnail),
            expire_time=expire_time,
        )
        response_thumbnails_data = {}
        response_thumbnails_data["img_url"] = (
            request.get_host() + "/i/" + time_limited_img.slug + "/"
        )
        return response_thumbnails_data
