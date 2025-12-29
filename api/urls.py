from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    OrganizationViewSet,
    LocationViewSet,
    AuthorProfileViewSet,
    BookViewSet,
    CategoryViewSet,
    BookApprovalViewSet,
    ConsignmentBatchViewSet,
    SaleViewSet,
    SalesImportViewSet,
    InventorySnapshotViewSet,
    InventoryTransactionViewSet,
    PaymentPeriodViewSet,
    AuthorBalanceViewSet,
    PayoutViewSet,
    AuthorLedgerViewSet,
    StaffDashboardViewSet,
)

router = DefaultRouter()

# Organizations & Locations
router.register(r"organizations", OrganizationViewSet, basename="organization")
router.register(r"locations", LocationViewSet, basename="location")

# Authors
router.register(r"authors", AuthorProfileViewSet, basename="author")

# Catalog
router.register(r"books", BookViewSet, basename="book")
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"book-approvals", BookApprovalViewSet, basename="book-approval")

# Consignment
router.register(r"consignment-batches", ConsignmentBatchViewSet, basename="consignment-batch")

# Sales & Inventory
router.register(r"sales", SaleViewSet, basename="sale")
router.register(r"sales-imports", SalesImportViewSet, basename="sales-import")
router.register(r"inventory", InventorySnapshotViewSet, basename="inventory")
router.register(r"inventory-transactions", InventoryTransactionViewSet, basename="inventory-transaction")

# Payouts
router.register(r"payment-periods", PaymentPeriodViewSet, basename="payment-period")
router.register(r"author-balances", AuthorBalanceViewSet, basename="author-balance")
router.register(r"payouts", PayoutViewSet, basename="payout")
router.register(r"author-ledger", AuthorLedgerViewSet, basename="author-ledger")

# Dashboards
router.register(r"staff-dashboard", StaffDashboardViewSet, basename="staff-dashboard")

app_name = "api"

urlpatterns = [
    path("", include(router.urls)),
]
