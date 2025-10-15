from django.contrib import admin
from .models import InventoryReceipt, Sale

@admin.register(InventoryReceipt)
class InventoryReceiptAdmin(admin.ModelAdmin):
    list_display = ("id","book","location","qty","unit_cost","received_at")
    list_filter = ("location","book")
    search_fields = ("book__title",)

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ("id","book","location","qty","unit_price","sold_at","source")
    list_filter = ("location","book")
    search_fields = ("book__title",)
