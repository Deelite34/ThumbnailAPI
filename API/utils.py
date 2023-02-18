import jwt
from django.utils.crypto import get_random_string
from rest_framework.authtoken.models import Token

from API import models
from ImageUploadAPI.settings import SECRET_KEY


def user_directory_path(instance, filename):
    """
    Used for specifying unique for each user file path of
    stored files, using his ID number.
    Usable in a imagefield model field, in upload_to parameter.
    """
    return "user_{0}/{1}".format(instance.owner.id, filename)


def set_image_model_slug(image, max_tries=10):
    """
    Generates and sets unique slug
    :param obj: object of GeneratedImage model
    """
    if not image.slug:
        image.slug = get_random_string(15)

    attempt = 0
    while models.Image.objects.filter(slug=image.slug).count() != 0:
        image.slug = get_random_string(15)
        attempt += 1
        if attempt >= 10:
            raise Exception(
                f"Failed to generate unique slug for image {str(max_tries)} times."
            )


def get_token_user_id(request):
    """Helper function to be used in view. Gets user id using JWT or DRF auth token"""
    request_token = request.META.get("HTTP_AUTHORIZATION", " ").split(" ")

    if request_token[0] == "Bearer":
        data = jwt.decode(jwt=request_token[1], key=SECRET_KEY, algorithms=["HS256"])
        token_user_id = data["user_id"]
    elif request_token[0] == "Token":
        token_user_id = Token.objects.get(key=request_token[1]).user_id
    return token_user_id
