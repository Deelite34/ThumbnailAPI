from django.contrib import admin

from .models import AccountTier, APIUser, Image


class AccountTierAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "tier_name",
        "allowed_thumbnail_sizes",
        "can_create_original_img_link",
        "can_create_time_limited_link",
    )


class APIUserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "account_type")


class ImageAdmin(admin.ModelAdmin):
    list_display = ("id", "owner", "image", "thumbnail_size", "expire_time", "created")


admin.site.register(AccountTier, AccountTierAdmin)
admin.site.register(APIUser, APIUserAdmin)
admin.site.register(Image, ImageAdmin)
