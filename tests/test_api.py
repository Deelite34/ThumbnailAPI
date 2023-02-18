import json
import os

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings

from API.models import Image
from tests.constants import (
    CONTENT_TYPE_DEFAULT,
    CONTENT_TYPE_PNG,
    ENDPOINT_ALL,
    ENDPOINT_TIMED,
    MOCK_WRONG_FILE_TYPE_PATH,
    TEST_IMAGE_PATH_A,
    TEST_IMAGE_PATH_B,
    TEST_IMAGE_PATH_BMP,
    TEST_IMAGE_PATH_C,
    TESTS_MEDIA_ROOT,
    TESTS_MEDIA_URL,
)

# allow all test functions to access test db
pytestmark = pytest.mark.django_db


# Decorator will cause test user directories and test images to be created in separate, easier to clean up directory
@override_settings(MEDIA_URL=TESTS_MEDIA_URL, MEDIA_ROOT=TESTS_MEDIA_ROOT)
def test_all_list_endpoint_receive_correct_response(
    basic_user, enterprise_user, client
):
    mock_image_a = SimpleUploadedFile(
        name=os.path.basename(TEST_IMAGE_PATH_A).split("/")[-1],
        content=open(TEST_IMAGE_PATH_A, "rb").read(),
        content_type=CONTENT_TYPE_PNG,
    )
    mock_image_b = SimpleUploadedFile(
        name=os.path.basename(TEST_IMAGE_PATH_B).split("/")[-1],
        content=open(TEST_IMAGE_PATH_B, "rb").read(),
        content_type=CONTENT_TYPE_PNG,
    )

    post_1_basic_user = client.post(
        ENDPOINT_ALL,
        data={"image": mock_image_a},
        HTTP_AUTHORIZATION=f"Token {basic_user['token']}",
        format="multipart",
    )
    post_2_basic_user = client.post(
        ENDPOINT_ALL,
        data={"image": mock_image_b},
        HTTP_AUTHORIZATION=f"Token {basic_user['token']}",
        format="multipart",
    )
    response = client.get(
        ENDPOINT_ALL, HTTP_AUTHORIZATION=f"Token {basic_user['token']}"
    )
    json_dict = json.loads(response.content)

    assert post_1_basic_user.status_code == 201
    assert post_2_basic_user.status_code == 201
    assert response.status_code == 200
    assert len(json_dict) == 2
    assert len(json_dict[0].keys()) == 3
    assert len(json_dict[1].keys()) == 3
    assert "http" in json_dict[0]["img_url"]


@override_settings(MEDIA_URL=TESTS_MEDIA_URL, MEDIA_ROOT=TESTS_MEDIA_ROOT)
def test_all_list_endpoint_can_see_only_own_images(basic_user, enterprise_user, client):
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
    response = client.get(
        ENDPOINT_ALL, HTTP_AUTHORIZATION=f"Token {enterprise_user['token']}"
    )
    json_dict = json.loads(response.content)

    assert response.status_code == 200
    assert len(json_dict) == 0


@override_settings(MEDIA_URL=TESTS_MEDIA_URL, MEDIA_ROOT=TESTS_MEDIA_ROOT)
def test_all_detail_endpoint_can_correctly_view_created_img_detail(
    basic_user, enterprise_user, client
):
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
    img_id = str(Image.objects.latest("id").id)
    get_1 = client.get(
        ENDPOINT_ALL + f"{img_id}/", HTTP_AUTHORIZATION=f"Token {basic_user['token']}"
    )
    response_dict = json.loads(get_1.content)

    assert get_1.status_code == 200
    assert len(response_dict) == 3


@override_settings(MEDIA_URL=TESTS_MEDIA_URL, MEDIA_ROOT=TESTS_MEDIA_ROOT)
def test_all_detail_endpoint_can_view_only_own_images(
    basic_user, enterprise_user, client
):
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
    img_id = str(Image.objects.latest("id").id)
    get_1 = client.get(
        ENDPOINT_ALL + f"{img_id}/",
        HTTP_AUTHORIZATION=f"Token {enterprise_user['token']}",
    )
    response_dict = json.loads(get_1.content)

    assert get_1.status_code == 404
    assert len(response_dict) == 1
    assert "detail" in response_dict.keys()


@override_settings(MEDIA_URL=TESTS_MEDIA_URL, MEDIA_ROOT=TESTS_MEDIA_ROOT)
def test_all_endpoint_creating_thumbnails_with_specific_account_tiers_response(
    basic_user, premium_user, enterprise_user, client
):
    mock_image_a = SimpleUploadedFile(
        name=os.path.basename(TEST_IMAGE_PATH_A).split("/")[-1],
        content=open(TEST_IMAGE_PATH_A, "rb").read(),
        content_type=CONTENT_TYPE_PNG,
    )
    mock_image_b = SimpleUploadedFile(
        name=os.path.basename(TEST_IMAGE_PATH_B).split("/")[-1],
        content=open(TEST_IMAGE_PATH_B, "rb").read(),
        content_type=CONTENT_TYPE_PNG,
    )
    mock_image_c = SimpleUploadedFile(
        name=os.path.basename(TEST_IMAGE_PATH_C).split("/")[-1],
        content=open(TEST_IMAGE_PATH_C, "rb").read(),
        content_type=CONTENT_TYPE_PNG,
    )

    basic_user_response = client.post(
        ENDPOINT_ALL,
        data={"image": mock_image_a},
        HTTP_AUTHORIZATION=f"Token {basic_user['token']}",
        format="multipart",
    )
    premium_user_response = client.post(
        ENDPOINT_ALL,
        data={"image": mock_image_b},
        HTTP_AUTHORIZATION=f"Token {premium_user['token']}",
        format="multipart",
    )
    enterprise_user_response = client.post(
        ENDPOINT_ALL,
        data={"image": mock_image_c},
        HTTP_AUTHORIZATION=f"Token {enterprise_user['token']}",
        format="multipart",
    )

    response_dict_basic_user = json.loads(basic_user_response.content.decode("utf8"))
    response_dict_premium_user = json.loads(
        premium_user_response.content.decode("utf8")
    )
    response_dict_enterprise_user = json.loads(
        enterprise_user_response.content.decode("utf8")
    )

    assert basic_user_response.status_code == 201
    assert len(response_dict_basic_user) == 4
    assert len(response_dict_basic_user["thumbnails"]) == 1
    assert "Upgrade account tier" in response_dict_basic_user["img_url"]

    assert premium_user_response.status_code == 201
    assert len(response_dict_premium_user) == 4
    assert len(response_dict_premium_user["thumbnails"]) == 3
    assert "http" in response_dict_premium_user["img_url"]

    assert enterprise_user_response.status_code == 201
    assert len(response_dict_enterprise_user) == 4
    assert len(response_dict_enterprise_user["thumbnails"]) == 3
    assert "http" in response_dict_enterprise_user["img_url"]


@override_settings(MEDIA_URL=TESTS_MEDIA_URL, MEDIA_ROOT=TESTS_MEDIA_ROOT)
def test_timed_endpoint_creating_timed_img_response(enterprise_user, client):
    mock_image = SimpleUploadedFile(
        name=os.path.basename(TEST_IMAGE_PATH_A).split("/")[-1],
        content=open(TEST_IMAGE_PATH_A, "rb").read(),
        content_type=CONTENT_TYPE_PNG,
    )
    request_body = {"image": mock_image, "thumbnail_size": "100", "expire_time": 300}

    enterprise_user_response = client.post(
        ENDPOINT_TIMED,
        data=request_body,
        HTTP_AUTHORIZATION=f"Token {enterprise_user['token']}",
        format="multipart",
    )
    response_dict = json.loads(enterprise_user_response.content.decode("utf8"))
    timed_image = Image.objects.latest("id")

    assert enterprise_user_response.status_code == 201
    assert timed_image.expire_time is not None
    assert len(response_dict) == 3


@override_settings(MEDIA_URL=TESTS_MEDIA_URL, MEDIA_ROOT=TESTS_MEDIA_ROOT)
def test_timed_endpoint_only_authorized_user_can_use_endpoint(
    basic_user, premium_user, client
):
    mock_image = SimpleUploadedFile(
        name=os.path.basename(TEST_IMAGE_PATH_A).split("/")[-1],
        content=open(TEST_IMAGE_PATH_A, "rb").read(),
        content_type=CONTENT_TYPE_PNG,
    )
    request_body = {"image": mock_image, "thumbnail_size": "100", "expire_time": 300}

    basic_user = client.post(
        ENDPOINT_TIMED,
        data=request_body,
        HTTP_AUTHORIZATION=f"Token {basic_user['token']}",
        format="multipart",
    )
    premium_user = client.post(
        ENDPOINT_TIMED,
        data=request_body,
        HTTP_AUTHORIZATION=f"Token {premium_user['token']}",
        format="multipart",
    )
    response_dict_basic_user = json.loads(basic_user.content.decode("utf8"))
    response_dict_premium_user = json.loads(premium_user.content.decode("utf8"))

    assert basic_user.status_code == 403
    assert len(response_dict_basic_user) == 1
    assert "error" in response_dict_basic_user.keys()
    assert premium_user.status_code == 403
    assert len(response_dict_premium_user) == 1
    assert "error" in response_dict_premium_user.keys()


@override_settings(MEDIA_URL=TESTS_MEDIA_URL, MEDIA_ROOT=TESTS_MEDIA_ROOT)
def test_all_endpoint_cant_access_without_token(basic_user, client):
    mock_image_a = SimpleUploadedFile(
        name=os.path.basename(TEST_IMAGE_PATH_A).split("/")[-1],
        content=open(TEST_IMAGE_PATH_A, "rb").read(),
        content_type=CONTENT_TYPE_PNG,
    )

    post_without_token_response = client.post(
        ENDPOINT_ALL,
        data={"image": mock_image_a},
        format="multipart",
    )
    get_without_token_response = client.get(ENDPOINT_ALL)
    post_response_dict = json.loads(post_without_token_response.content.decode("utf8"))
    get_response_dict = json.loads(get_without_token_response.content.decode("utf8"))

    assert post_without_token_response.status_code == 401
    assert len(post_response_dict) == 1
    assert "detail" in post_response_dict.keys()
    assert get_without_token_response.status_code == 401
    assert len(get_response_dict) == 1
    assert "detail" in get_response_dict.keys()


@override_settings(MEDIA_URL=TESTS_MEDIA_URL, MEDIA_ROOT=TESTS_MEDIA_ROOT)
def test_detail_endpoint_cant_access_without_token(basic_user, client):
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
    img_id = str(Image.objects.latest("id").id)
    get_response = client.get(ENDPOINT_ALL + f"{img_id}/")
    get_response_dict = json.loads(get_response.content.decode("utf8"))

    assert get_response.status_code == 401
    assert len(get_response_dict) == 1
    assert "detail" in get_response_dict.keys()


@override_settings(MEDIA_URL=TESTS_MEDIA_URL, MEDIA_ROOT=TESTS_MEDIA_ROOT)
def test_response_for_request_with_incorrect_fields(
    basic_user, enterprise_user, client
):
    response_incorrect_data_all = client.post(
        ENDPOINT_ALL,
        {"dataaa": "asdf"},
        HTTP_AUTHORIZATION=f"Token {basic_user['token']}",
    )
    response_incorrect_data_timed = client.post(
        ENDPOINT_TIMED,
        {"dataaa": "qwe"},
        HTTP_AUTHORIZATION=f"Token {enterprise_user['token']}",
    )
    response_all_dict = json.loads(response_incorrect_data_all.content.decode("utf8"))
    response_timed_dict = json.loads(
        response_incorrect_data_timed.content.decode("utf8")
    )

    assert len(response_all_dict) == 1
    assert "image" in response_all_dict.keys()
    assert len(response_timed_dict) == 3
    assert "image" in response_timed_dict.keys()
    assert "thumbnail_size" in response_timed_dict.keys()
    assert "expire_time" in response_timed_dict.keys()


@override_settings(MEDIA_URL=TESTS_MEDIA_URL, MEDIA_ROOT=TESTS_MEDIA_ROOT)
def test_all_endpoint_upload_not_a_image(basic_user, client):
    incorrect_file = SimpleUploadedFile(
        name=os.path.basename(MOCK_WRONG_FILE_TYPE_PATH).split("/")[-1],
        content=open(MOCK_WRONG_FILE_TYPE_PATH, "rb").read(),
        content_type=CONTENT_TYPE_DEFAULT,
    )

    response = client.post(
        ENDPOINT_ALL,
        {"image": incorrect_file},
        HTTP_AUTHORIZATION=f"Token {basic_user['token']}",
        format="multipart",
    )
    json_dict = json.loads(response.content.decode("utf8"))

    assert response.status_code == 400
    assert len(json_dict) == 1
    assert "image" in json_dict.keys()


@override_settings(MEDIA_URL=TESTS_MEDIA_URL, MEDIA_ROOT=TESTS_MEDIA_ROOT)
def test_all_endpoint_check_validation_for_unsupported_image_type(basic_user, client):
    """Checks used custom file type validator"""
    unsupported_image_format = SimpleUploadedFile(
        name=os.path.basename(TEST_IMAGE_PATH_BMP).split("/")[-1],
        content=open(TEST_IMAGE_PATH_BMP, "rb").read(),
    )
    response = client.post(
        ENDPOINT_ALL,
        {"image": unsupported_image_format},
        HTTP_AUTHORIZATION=f"Token {basic_user['token']}",
        format="multipart",
    )
    json_dict = json.loads(response.content.decode("utf8"))

    assert response.status_code == 400
    assert len(json_dict) == 1
    assert "image" in json_dict.keys()
    assert "Incorrect file type. Allowed types" in json_dict["image"][0]
