from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework import status, viewsets
from rest_framework.authtoken.admin import User
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from API.models import APIUser, Image
from API.serializers import ImageSerializer, TimeLimitedImageSerializer
from API.utils import get_token_user_id


class ImageUploadView(viewsets.ViewSet):
    """
    User can send POST request with auth token in header to the endpoint /api/thumbnail/.
    POST request should include .jpg or .png image file.
    """

    serializer_class = ImageSerializer
    permission_classes = (IsAuthenticated,)

    @extend_schema(  # drf-spectacular documentation extension
        responses={200: OpenApiTypes.OBJECT, 401: OpenApiTypes.OBJECT},
        examples=[
            OpenApiExample(
                "200 OK",
                description="Get all owned images.",
                value=[
                    {
                        "id": 1,
                        "img_url": "localhost:1337/i/fsomeCslug3aoqA/",
                        "img_size": "720x619",
                    },
                    {
                        "id": 2,
                        "img_url": "localhost:1337/i/fsomeCslug3qwer/",
                        "img_size": "200x200",
                    },
                ],
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                "401 No authorization provided",
                description="Response when user does not provide token or jwt token in request header",
                value={"detail": "Authentication credentials were not provided."},
                response_only=True,
                status_codes=["401"],
            ),
        ],
    )
    def list(self, request):
        """
        Lists all images and related thumbnails for specific user. Auth or JWT token is required.
        """
        token_user_id = get_token_user_id(request)
        queryset = Image.objects.filter(owner=token_user_id)
        serializer = ImageSerializer(queryset, many=True, context={"request": request})
        return Response(serializer.data)

    @extend_schema(  # drf-spectacular documentation extension
        parameters=[
            OpenApiParameter(
                name="id",
                location=OpenApiParameter.PATH,
                description="ID number of image passed through url",
                required=True,
            )
        ],
        responses={
            200: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
        examples=[
            OpenApiExample(
                "request body",
                description="Attached image be of png or jpg type, or validation will fail",
                value={"image": "<attached file>"},
                request_only=True,
            ),
            OpenApiExample(
                "200 thumbnail retrieved successfully",
                description="Token of image owner is provided, and image exists.",
                value={
                    "id": 1,
                    "img_url": "localhost:1337/i/someQWERTYUslug/",
                    "img_size": "720x619",
                },
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                "401 No authorization provided",
                description="Response when user does not provide token or jwt token in request header",
                value={"detail": "Authentication credentials were not provided."},
                response_only=True,
                status_codes=["401"],
            ),
            OpenApiExample(
                "404 thumbnail not found",
                description="Response when image with id does not exist or is not owned by user.",
                value={"detail": "Item not found"},
                response_only=True,
                status_codes=["404"],
            ),
        ],
    )
    def retrieve(self, request, pk=None):
        """
        Display information about specific uploaded image
        """
        token_user_id = get_token_user_id(request)

        try:
            queryset = Image.objects.get(owner=token_user_id, id=pk)
        except Image.DoesNotExist:
            return Response(
                {"detail": "Item not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = ImageSerializer(queryset, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(  # drf-spectacular documentation extension
        parameters=[
            OpenApiParameter(
                name="image",
                location=OpenApiParameter.QUERY,
                description="attached image",
                required=True,
            )
        ],
        responses={
            201: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
        },
        examples=[
            OpenApiExample(
                "request body",
                description="Image must be an image of png or jpg type.",
                value={"Image": "<attached image file>"},
                request_only=True,
            ),
            OpenApiExample(
                "201 Thumbnail created",
                description="Thumbnails assigned to account tier will be created and returned. "
                "Original image link will be there only if account tier settings permit it.",
                value={
                    "id": 1,
                    "img_url": "localhost:1337/i/someQWEslugRT/",
                    "img_size": "720x619",
                    "thumbnails": {
                        "200": "localhost:1337/i/someASDslugRT/",
                        "400": "localhost:1337/i/someZXCslugRT//",
                        "720x619": "localhost:1337/i/someBNMslugRT/",
                    },
                },
                response_only=True,
                status_codes=["201"],
            ),
            OpenApiExample(
                "400 No image parameter",
                description="Response when 'image' parameter is not included.",
                value={"image": ["No file was submitted."]},
                response_only=True,
                status_codes=["400"],
            ),
            OpenApiExample(
                "401",
                description="Response when user does not provide token or jwt token in request header, required to authorize and identify him.",
                value={"detail": "Authentication credentials were not provided."},
                response_only=True,
                status_codes=["401"],
            ),
        ],
    )
    def create(self, request):
        token_user_id = get_token_user_id(request)
        token_user = APIUser.objects.get(id=token_user_id)

        serializer = ImageSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=token_user)

        user = APIUser.objects.select_related("account_type").get(id=token_user_id)
        original_img = Image.objects.filter(owner=token_user_id).latest("id")

        response_thumbnails = original_img.make_thumbnails(user, request)

        updated_serializer_data = serializer.data
        updated_serializer_data.update(response_thumbnails)
        return Response(updated_serializer_data, status=status.HTTP_201_CREATED)


class TimeLimitedThumbnailView(viewsets.ViewSet):
    serializer_class = TimeLimitedImageSerializer
    permission_classes = (IsAuthenticated,)

    @extend_schema(  # drf-spectacular documentation extension
        parameters=[
            OpenApiParameter(
                name="image",
                location=OpenApiParameter.QUERY,
                description="attached image",
                required=True,
            ),
            OpenApiParameter(
                name="thumbnail_size",
                location=OpenApiParameter.QUERY,
                description="integer",
                required=True,
            ),
            OpenApiParameter(
                name="expire_time",
                location=OpenApiParameter.QUERY,
                description="integer",
                required=True,
            ),
        ],
        responses={
            201: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
            403: OpenApiTypes.OBJECT,
        },
        examples=[
            OpenApiExample(
                "request body",
                description="File must be an image of png or jpg type. Thumbnail size describes length of side of the square thumbnail."
                "Image will expire after time included in expire_time parameter. ",
                value={
                    "image": "<attached Image>",
                    "thumbnail_size": "integer",
                    "expire_time": "integer",
                },
                request_only=True,
            ),
            OpenApiExample(
                "201 Thumbnail created",
                description="Example response when thumbnail gets created successfully.",
                value={
                    "thumbnail_size": 50,
                    "expire_time": 300,
                    "img_url": "localhost:1337/i/someQWERTslug5T/",
                },
                response_only=True,
                status_codes=["201"],
            ),
            OpenApiExample(
                "400 No file parameter",
                description="Response when 'file' parameter is not included.",
                value={"image": ["No file was submitted."]},
                response_only=True,
                status_codes=["400"],
            ),
            OpenApiExample(
                "400 No type or expire_time parameter",
                description="Response either or both 'type' or 'expire_time' parameters are not included.",
                value={
                    "thumbnail_size": "This field is required.",
                    "expire_time": "This field is required.",
                },
                response_only=True,
                status_codes=["400"],
            ),
            OpenApiExample(
                "401 No authorization provided",
                description="Response when user does not provide token or jwt token in request header",
                value={"detail": "Authentication credentials were not provided."},
                response_only=True,
                status_codes=["401"],
            ),
            OpenApiExample(
                "403 Permission error",
                description="Response when user profile type is not allowed to create time limited thumbnails.",
                value={
                    "error": "Upgrade your account, to access time limited thumbnails"
                },
                response_only=True,
                status_codes=["403"],
            ),
        ],
    )
    def create(self, request):
        """
        Checks authorization of user, then creates a time limited thumbnail if user permission allows it
        """
        token_user_id = get_token_user_id(request)
        token_user = APIUser.objects.get(id=token_user_id)
        user = APIUser.objects.select_related("account_type").get(id=token_user_id)

        if not user.account_type.can_create_time_limited_link:
            return Response(
                {"error": "Upgrade your account, to access time limited thumbnails"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = TimeLimitedImageSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=token_user)

        expire_time = serializer.data["expire_time"]
        thumbnail_size = serializer.data["thumbnail_size"]

        source_image = Image.objects.filter(owner=token_user_id).latest("id")
        response_thumbnail = source_image.make_time_limited_thumbnail(
            user, request, expire_time, thumbnail_size
        )

        updated_serializer_data = serializer.data
        updated_serializer_data.update(response_thumbnail)
        return Response(updated_serializer_data, status=status.HTTP_201_CREATED)
