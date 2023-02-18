import os

from ImageUploadAPI.settings import BASE_DIR

TEST_USER_LOGIN = "test_user"
TEST_USER_PASS = "qwerty12345"
TEST_TIER_TYPE_NAME = "test_tier_type"
ENDPOINT_ALL = "/api/v1/thumbnails/all/"
ENDPOINT_TIMED = "/api/v1/thumbnails/timed/"
TEST_IMAGE_PATH_A = os.path.join(
    os.getcwd(), "tests", "helper_files", "test_image_a.png"
)
TEST_IMAGE_PATH_B = os.path.join(
    os.getcwd(), "tests", "helper_files", "test_image_b.png"
)
TEST_IMAGE_PATH_C = os.path.join(
    os.getcwd(), "tests", "helper_files", "test_image_c.png"
)
TEST_IMAGE_PATH_PNG = os.path.join(
    os.getcwd(), "tests", "helper_files", "test_image_a.png"
)
TEST_IMAGE_PATH_JPG = os.path.join(
    os.getcwd(), "tests", "helper_files", "test_image_d.jpg"
)
TEST_IMAGE_PATH_BMP = os.path.join(
    os.getcwd(), "tests", "helper_files", "test_image_e.bmp"
)
MOCK_WRONG_FILE_TYPE_PATH = os.path.join(
    os.getcwd(), "tests", "helper_files", "test_text.txt"
)
TEST_MEDIA_IMAGE_PATH_A = os.path.join(
    os.getcwd(), "tests", "tests_media", "test_image_a.png"
)
CONTENT_TYPE_PNG = "image/png"
CONTENT_TYPE_DEFAULT = "text/plain"
TESTS_MEDIA_ROOT = os.path.join(BASE_DIR, "tests", "tests_media")
TESTS_MEDIA_URL = "/tests_media/"
