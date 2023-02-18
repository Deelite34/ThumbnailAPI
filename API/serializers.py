from rest_framework import serializers

from API.models import Image


class ImageSerializer(serializers.ModelSerializer):
    queryset = Image.objects.all()
    img_url = serializers.SerializerMethodField()
    img_size = serializers.SerializerMethodField()

    class Meta:
        model = Image
        fields = ["id", "image", "img_url", "img_size"]
        extra_kwargs = {
            "image": {"write_only": True},
        }

    def get_img_url(self, image: Image):
        """Gets urls for generated images"""
        request = self.context.get("request")
        if (
            not request.user.account_type.can_create_original_img_link
            and not image.thumbnail_size
        ):
            return "Upgrade account tier to obtain original image link."
        slug = image.slug
        image_url = request.get_host() + "/i/" + slug + "/"
        return request.build_absolute_uri(image_url)

    def get_img_size(self, generated_image: Image):
        return f"{generated_image.image.width}x{generated_image.image.height}"


class TimeLimitedImageSerializer(serializers.ModelSerializer):
    """
    When user sends expire_time and type fields with other data to serializer, those fields are used only in
    the view, to generate specified thumbnails.
    """

    queryset = Image.objects.all()

    expire_time = serializers.IntegerField(min_value=300, max_value=30000)
    thumbnail_size = serializers.IntegerField(min_value=50, max_value=4000)

    class Meta:
        model = Image
        fields = ["image", "thumbnail_size", "expire_time"]
        extra_kwargs = {
            "image": {"write_only": True},
        }
