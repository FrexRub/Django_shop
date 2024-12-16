from django.contrib import admin

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    ordering = ("id",)
    list_display = ("id", "name_profile")
    list_display_links = (
        "id",
        "name_profile",
    )

    def name_profile(self, obj: Profile):
        return (
            f"{obj.user.username} ({obj.user.first_name})"
            if obj.user.first_name
            else f"{obj.user.username}"
        )
