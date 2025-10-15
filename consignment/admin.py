from django.contrib import admin
from .models import ConsignmentAgreement

@admin.register(ConsignmentAgreement)
class ConsignmentAgreementAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "book", "author_share", "start", "end")
    list_filter = ("author", "book")
