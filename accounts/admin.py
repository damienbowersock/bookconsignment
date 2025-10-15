from django.contrib import admin
from .models import Organization, Location, AuthorProfile

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("id", "name")

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "org")
    list_filter = ("org",)

@admin.register(AuthorProfile)
class AuthorProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "org", "phone")
    list_filter = ("org",)
