import datetime
import os

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse

from API.models import Image
from tests.constants import (
    CONTENT_TYPE_PNG,
    ENDPOINT_ALL,
    TEST_IMAGE_PATH_A,
    TESTS_MEDIA_ROOT,
    TESTS_MEDIA_URL,
)

pytestmark = pytest.mark.django_db  # all test functions can access db


@override_settings(MEDIA_URL=TESTS_MEDIA_URL, MEDIA_ROOT=TESTS_MEDIA_ROOT)
def test_display_image_correctly(basic_user, client):
    mock_image_a = SimpleUploadedFile(
        name=os.path.basename(TEST_IMAGE_PATH_A).split("/")[-1],
        content=open(TEST_IMAGE_PATH_A, "rb").read(),
        content_type=CONTENT_TYPE_PNG,
    )

    client.post(
        ENDPOINT_ALL,
        data={"image": mock_image_a},
        HTTP_AUTHORIZATION=f"Token {basic_user['token']}",
        format="multipart",
    )
    img = Image.objects.latest("id")
    image_page_response = client.get(reverse("display_image", args=[img.slug]))

    assert image_page_response.status_code == 200
    assert not ("expired" in image_page_response.content.decode("utf8"))


@override_settings(MEDIA_URL=TESTS_MEDIA_URL, MEDIA_ROOT=TESTS_MEDIA_ROOT)
@pytest.fixture(params=[datetime.datetime(2030, 12, 25, 17, 5, 55)])
def test_dont_display_expired_image(basic_user, client):
    mock_image_a = SimpleUploadedFile(
        name=os.path.basename(TEST_IMAGE_PATH_A).split("/")[-1],
        content=open(TEST_IMAGE_PATH_A, "rb").read(),
        content_type=CONTENT_TYPE_PNG,
    )

    client.post(
        ENDPOINT_ALL,
        data={"image": mock_image_a},
        HTTP_AUTHORIZATION=f"Token {basic_user['token']}",
        format="multipart",
    )
    img = Image.objects.latest("id")
    image_page_response = client.get(reverse("display_image", args=[img.slug]))

    assert image_page_response.status_code == 200
    assert "expired" in image_page_response.content.decode("utf8")
