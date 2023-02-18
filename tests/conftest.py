import os
import shutil
from random import randint

import pytest
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from API.models import AccountTier, APIUser
from ImageUploadAPI.settings import TEST_API_DIR, TESTS_MEDIA_DIR
from tests.constants import TEST_USER_LOGIN, TEST_USER_PASS


@pytest.fixture(scope="session", autouse=True)
def setup_and_teardown():
    """Move to /API/test directory  before tests start, to ensure access to test image file"""

    yield
    # Things to be executed after the last test
    print("Cleaning up created test thumbnails..")
    folders = os.listdir(TESTS_MEDIA_DIR)
    for folder in folders:
        directory = TESTS_MEDIA_DIR + "/" + folder
        if os.path.isdir(directory):
            print("Removing: " + directory)
            shutil.rmtree(directory)


@pytest.fixture
def test_client(user, authorization_header=True):
    """
    Creates APIClient, and authorizes it with a token
    :return: client - APIClient instance authorized with token
    """
    client = APIClient()

    if authorization_header:
        token = Token.objects.create(user=user)
        client.credentials(HTTP_AUTHORIZATION="Token " + token.key)
    return client


@pytest.fixture
def basic_tier(db) -> AccountTier:
    return AccountTier.objects.create(
        tier_name="basic",
        allowed_thumbnail_sizes=[200],
        can_create_original_img_link=False,
        can_create_time_limited_link=False,
    )


@pytest.fixture
def premium_tier(db) -> AccountTier:
    return AccountTier.objects.create(
        tier_name="premium",
        allowed_thumbnail_sizes=[200, 400],
        can_create_original_img_link=True,
        can_create_time_limited_link=False,
    )


@pytest.fixture
def enterprise_tier(db) -> AccountTier:
    return AccountTier.objects.create(
        tier_name="enterprise",
        allowed_thumbnail_sizes=[200, 400],
        can_create_original_img_link=True,
        can_create_time_limited_link=True,
    )


@pytest.fixture
def basic_user(db, basic_tier) -> APIUser:
    user = APIUser.objects.create_user(
        username=TEST_USER_LOGIN + f"_{str(randint(0, 999999))}",
        password=TEST_USER_PASS,
        account_type=basic_tier,
    )
    token = Token.objects.create(user=user)
    return {"user": user, "token": token}


@pytest.fixture
def premium_user(db, premium_tier) -> APIUser:
    user = APIUser.objects.create_user(
        username=TEST_USER_LOGIN + f"_{str(randint(0, 999999))}",
        password=TEST_USER_PASS,
        account_type=premium_tier,
    )
    token = Token.objects.create(user=user)
    return {"user": user, "token": token}


@pytest.fixture
def enterprise_user(db, enterprise_tier) -> APIUser:
    user = APIUser.objects.create_user(
        username=TEST_USER_LOGIN + f"_{str(randint(0, 999999))}",
        password=TEST_USER_PASS,
        account_type=enterprise_tier,
    )
    token = Token.objects.create(user=user)
    return {"user": user, "token": token}
