from django.contrib import admin
from .models import Organization, Location, AuthorProfile, StaffProfile, AuthorOrganization


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug", "city", "state", "default_author_share", "payment_cycle", "is_active")
    list_filter = ("is_active", "payment_cycle")
    search_fields = ("name", "slug", "city")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at")


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "org", "city", "state", "is_active")
    list_filter = ("org", "is_active")
    search_fields = ("name", "city")
    readonly_fields = ("created_at", "updated_at")


@admin.register(AuthorProfile)
class AuthorProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "full_name", "email", "phone", "preferred_payment_method", "is_active")
    list_filter = ("is_active", "preferred_payment_method")
    search_fields = ("user__username", "user__email", "user__first_name", "user__last_name")
    readonly_fields = ("created_at", "updated_at")


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "org", "role", "phone", "is_active")
    list_filter = ("org", "role", "is_active")
    search_fields = ("user__username", "user__email", "user__first_name", "user__last_name")
    filter_horizontal = ("locations",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(AuthorOrganization)
class AuthorOrganizationAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "org", "status", "author_share_override", "joined_at")
    list_filter = ("org", "status")
    search_fields = ("author__user__username", "author__user__first_name", "author__user__last_name")
    readonly_fields = ("joined_at", "created_at", "updated_at")
