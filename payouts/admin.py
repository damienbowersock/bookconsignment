from django.contrib import admin
from .models import Payout

@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    list_display = ("id","author","amount","method","reference","paid_at")
    list_filter = ("method", "author")
    search_fields = ("author__user__username","author__user__first_name","author__user__last_name")
