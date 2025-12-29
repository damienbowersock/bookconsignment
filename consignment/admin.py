from django.contrib import admin
from .models import ConsignmentBatch, ConsignmentItem, ConsignmentReturn, ConsignmentReturnItem


class ConsignmentItemInline(admin.TabularInline):
    model = ConsignmentItem
    extra = 0
    readonly_fields = ("quantity_sold", "quantity_returned", "quantity_damaged", "created_at")


@admin.register(ConsignmentBatch)
class ConsignmentBatchAdmin(admin.ModelAdmin):
    list_display = (
        "id", "batch_number", "author", "org", "location",
        "received_date", "status", "consignment_end_date"
    )
    list_filter = ("org", "location", "status")
    search_fields = (
        "batch_number", "author__user__first_name", "author__user__last_name"
    )
    readonly_fields = ("consignment_end_date", "created_at", "updated_at")
    inlines = [ConsignmentItemInline]


@admin.register(ConsignmentItem)
class ConsignmentItemAdmin(admin.ModelAdmin):
    list_display = (
        "id", "book", "batch", "quantity_consigned",
        "quantity_sold", "quantity_returned", "quantity_damaged"
    )
    list_filter = ("batch__org", "batch__location")
    search_fields = ("book__title", "book__isbn")
    readonly_fields = ("quantity_sold", "quantity_returned", "quantity_damaged", "created_at", "updated_at")


class ConsignmentReturnItemInline(admin.TabularInline):
    model = ConsignmentReturnItem
    extra = 0


@admin.register(ConsignmentReturn)
class ConsignmentReturnAdmin(admin.ModelAdmin):
    list_display = ("id", "batch", "returned_date", "reason")
    list_filter = ("reason",)
    readonly_fields = ("created_at", "updated_at")
    inlines = [ConsignmentReturnItemInline]
