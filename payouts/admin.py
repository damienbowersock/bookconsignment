from django.contrib import admin
from .models import PaymentPeriod, AuthorBalance, Payout, PayoutLineItem, AuthorLedger


class AuthorBalanceInline(admin.TabularInline):
    model = AuthorBalance
    extra = 0
    readonly_fields = ("sales_total", "earnings_total", "amount_paid", "status")


@admin.register(PaymentPeriod)
class PaymentPeriodAdmin(admin.ModelAdmin):
    list_display = (
        "id", "org", "name", "period_start", "period_end",
        "status", "total_sales", "total_author_earnings"
    )
    list_filter = ("org", "status")
    readonly_fields = (
        "total_sales", "total_author_earnings", "total_store_earnings",
        "closed_at", "created_at", "updated_at"
    )
    inlines = [AuthorBalanceInline]


@admin.register(AuthorBalance)
class AuthorBalanceAdmin(admin.ModelAdmin):
    list_display = (
        "id", "author", "org", "period", "earnings_total",
        "amount_paid", "balance_due", "status"
    )
    list_filter = ("org", "status")
    search_fields = (
        "author__user__first_name", "author__user__last_name",
        "author__user__username"
    )
    readonly_fields = ("created_at", "updated_at")


class PayoutLineItemInline(admin.TabularInline):
    model = PayoutLineItem
    extra = 0


@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    list_display = (
        "id", "author", "org", "amount", "method",
        "status", "paid_at", "reference"
    )
    list_filter = ("org", "method", "status")
    search_fields = (
        "author__user__username", "author__user__first_name",
        "author__user__last_name", "reference"
    )
    readonly_fields = ("paid_at", "confirmed_at", "created_at", "updated_at")
    inlines = [PayoutLineItemInline]


@admin.register(AuthorLedger)
class AuthorLedgerAdmin(admin.ModelAdmin):
    list_display = (
        "id", "author", "org", "entry_type", "amount",
        "balance_after", "entry_date"
    )
    list_filter = ("org", "entry_type")
    search_fields = (
        "author__user__first_name", "author__user__last_name",
        "description"
    )
    readonly_fields = ("created_at",)
    date_hierarchy = "entry_date"
