from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, TrainerProfile, AthleteProfile


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # show the role field in admin
    fieldsets = UserAdmin.fieldsets + (
        ("Role info", {"fields": ("role",)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Role info", {"fields": ("role",)}),
    )
    list_display = ("username", "email", "first_name",
                    "last_name", "role", "is_staff")
    list_filter = ("role", "is_staff", "is_superuser", "is_active")


@admin.register(TrainerProfile)
class TrainerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "organization_name", "pass_key")
    search_fields = ("user__username", "organization_name", "pass_key")


@admin.register(AthleteProfile)
class AthleteProfileAdmin(admin.ModelAdmin):
    list_display = ("user",)
    search_fields = ("user__username",)
    filter_horizontal = ("trainers",)
