from django.contrib import admin
from .models import Book, Category, BookApproval


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "author", "isbn", "retail_price", "format", "is_active")
    list_filter = ("author", "format", "is_active")
    search_fields = ("title", "isbn", "isbn13", "author__user__first_name", "author__user__last_name")
    filter_horizontal = ("categories",)
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {
            "fields": ("author", "title", "subtitle", "description")
        }),
        ("Identifiers", {
            "fields": ("isbn", "isbn13", "sku")
        }),
        ("Pricing", {
            "fields": ("retail_price", "wholesale_price")
        }),
        ("Physical Attributes", {
            "fields": ("format", "page_count", "dimensions", "weight_oz")
        }),
        ("Cover", {
            "fields": ("cover_image", "cover_image_url")
        }),
        ("Publication", {
            "fields": ("publisher", "publication_date", "edition", "language")
        }),
        ("Categories", {
            "fields": ("categories",)
        }),
        ("Status", {
            "fields": ("is_active", "created_at", "updated_at")
        }),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug", "parent")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(BookApproval)
class BookApprovalAdmin(admin.ModelAdmin):
    list_display = ("id", "book", "org", "status", "reviewed_at", "reviewed_by")
    list_filter = ("org", "status")
    search_fields = ("book__title", "book__isbn")
    readonly_fields = ("created_at", "updated_at")
