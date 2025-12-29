from django.contrib import admin
from .models import Sale, SalesImport, InventoryTransaction, InventorySnapshot


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = (
        "id", "book", "location", "quantity", "unit_price",
        "author_share_rate", "author_earnings", "sold_at", "source"
    )
    list_filter = ("org", "location", "source")
    search_fields = ("book__title", "book__isbn", "external_id")
    readonly_fields = ("author_earnings", "created_at", "updated_at")
    date_hierarchy = "sold_at"


@admin.register(SalesImport)
class SalesImportAdmin(admin.ModelAdmin):
    list_display = (
        "id", "original_filename", "org", "location", "status",
        "total_rows", "success_count", "error_count", "created_at"
    )
    list_filter = ("org", "status", "source")
    readonly_fields = (
        "file_size", "total_rows", "processed_rows", "success_count",
        "error_count", "started_at", "completed_at", "created_at", "updated_at"
    )


@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "id", "book", "location", "transaction_type",
        "quantity_change", "quantity_after", "transaction_date"
    )
    list_filter = ("org", "location", "transaction_type")
    search_fields = ("book__title", "book__isbn")
    readonly_fields = ("created_at",)
    date_hierarchy = "transaction_date"


@admin.register(InventorySnapshot)
class InventorySnapshotAdmin(admin.ModelAdmin):
    list_display = (
        "id", "book", "location", "quantity_on_hand",
        "quantity_available", "total_sold", "last_sold_at"
    )
    list_filter = ("org", "location")
    search_fields = ("book__title", "book__isbn")
    readonly_fields = (
        "quantity_on_hand", "quantity_available", "total_received",
        "total_sold", "total_returned_author", "total_damaged",
        "last_received_at", "last_sold_at", "created_at", "updated_at"
    )
