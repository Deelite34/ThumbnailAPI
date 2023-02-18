import datetime
import os

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse

from API.models import AccountTier, Image
from tests.constants import (
    TEST_IMAGE_PATH_A,
    TEST_MEDIA_IMAGE_PATH_A,
    TESTS_MEDIA_ROOT,
    TESTS_MEDIA_URL,
)

pytestmark = pytest.mark.django_db


@override_settings(MEDIA_URL=TESTS_MEDIA_URL, MEDIA_ROOT=TESTS_MEDIA_ROOT)
def test_account_tier_to_string():
    name = "name"

    tier = AccountTier.objects.create(tier_name=name, allowed_thumbnail_sizes=[200])

    assert str(tier) == name


@override_settings(MEDIA_URL=TESTS_MEDIA_URL, MEDIA_ROOT=TESTS_MEDIA_ROOT)
def test_apiuser_to_string(basic_user):
    assert str(basic_user["user"]) == f"{basic_user['user'].username}"


@override_settings(MEDIA_URL=TESTS_MEDIA_URL, MEDIA_ROOT=TESTS_MEDIA_ROOT)
def test_image_to_string(basic_user):
    image = Image.objects.create(
        owner=basic_user["user"],
        image=TEST_IMAGE_PATH_A,
    )

    assert str(image) == f"{os.path.basename(image.image.url)}"


@override_settings(MEDIA_URL=TESTS_MEDIA_URL, MEDIA_ROOT=TESTS_MEDIA_ROOT)
def test_image_save(basic_user):
    image = Image(
        owner=basic_user["user"],
        image=TEST_IMAGE_PATH_A,
    )
    image.save()

    assert image.slug is not None


@override_settings(MEDIA_URL=TESTS_MEDIA_URL, MEDIA_ROOT=TESTS_MEDIA_ROOT)
@pytest.fixture(params=[datetime.datetime(2055, 12, 25, 17, 5, 55)])
def test_image_property_is_expired(basic_user):
    image = Image.objects.create(
        owner=basic_user["user"], image=TEST_IMAGE_PATH_A, expire_time=400
    )

    assert image.is_expired is True


@override_settings(MEDIA_URL=TESTS_MEDIA_URL, MEDIA_ROOT=TESTS_MEDIA_ROOT)
def test_image_property_is_not_expired(basic_user):
    image = Image.objects.create(
        owner=basic_user["user"], image=TEST_IMAGE_PATH_A, expire_time=400
    )

    assert image.is_expired is False


@override_settings(MEDIA_URL=TESTS_MEDIA_URL, MEDIA_ROOT=TESTS_MEDIA_ROOT)
def test_image_property_is_not_expired(basic_user):
    image = Image.objects.create(
        owner=basic_user["user"], image=TEST_IMAGE_PATH_A, expire_time=400
    )

    assert image.is_expired is False


@override_settings(MEDIA_URL=TESTS_MEDIA_URL, MEDIA_ROOT=TESTS_MEDIA_ROOT)
def test_image_get_url(basic_user, client):
    response = client.get(reverse("all-list"))
    request = response.wsgi_request
    image = Image.objects.create(
        owner=basic_user["user"], image=TEST_IMAGE_PATH_A, expire_time=400
    )

    assert image.get_url(request) == request.get_host() + "/i/" + image.slug + "/"


@override_settings(MEDIA_URL=TESTS_MEDIA_URL, MEDIA_ROOT=TESTS_MEDIA_ROOT)
def test_image_make_thumbnails(premium_user, client):
    image = Image.objects.create(
        owner=premium_user["user"],
        image=TEST_MEDIA_IMAGE_PATH_A,
    )
    response = client.get(reverse("all-list"))
    request = response.wsgi_request

    images_dict = image.make_thumbnails(premium_user["user"], request)
    all_images = Image.objects.all()

    assert all_images.count() == 3
    for image in all_images:
        assert image.slug is not None
    assert "thumbnails" in images_dict
    assert len(images_dict["thumbnails"]) == 3


@override_settings(MEDIA_URL=TESTS_MEDIA_URL, MEDIA_ROOT=TESTS_MEDIA_ROOT)
def test_image_make_time_limited_thumbnail(enterprise_user, client):
    image = Image.objects.create(
        owner=enterprise_user["user"],
        image=TEST_MEDIA_IMAGE_PATH_A,
    )
    response = client.get(reverse("all-list"))
    request = response.wsgi_request

    image_dict = image.make_time_limited_thumbnail(
        enterprise_user["user"], request, 300, 400
    )
    all_images = Image.objects.all()

    assert all_images.count() == 2
    for image in all_images:
        assert image.slug is not None
    assert "img_url" in image_dict
    assert len(image_dict) == 1
