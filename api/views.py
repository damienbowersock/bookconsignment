from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Sum, F, Q
from django.utils import timezone
from decimal import Decimal
import csv
import io

from accounts.models import (
    Organization, Location, AuthorProfile, StaffProfile, AuthorOrganization
)
from catalog.models import Book, Category, BookApproval
from consignment.models import ConsignmentBatch, ConsignmentItem
from sales.models import Sale, SalesImport, InventoryTransaction, InventorySnapshot
from payouts.models import PaymentPeriod, AuthorBalance, Payout, PayoutLineItem, AuthorLedger

from .serializers import (
    OrganizationSerializer, OrganizationListSerializer,
    LocationSerializer,
    AuthorProfileSerializer, AuthorProfileCreateSerializer, AuthorListSerializer,
    StaffProfileSerializer,
    AuthorOrganizationSerializer,
    BookSerializer, BookListSerializer,
    CategorySerializer,
    BookApprovalSerializer,
    ConsignmentBatchSerializer, ConsignmentBatchListSerializer,
    ConsignmentItemSerializer,
    SaleSerializer, SaleListSerializer,
    SalesImportSerializer,
    InventorySnapshotSerializer, InventoryTransactionSerializer,
    PaymentPeriodSerializer,
    AuthorBalanceSerializer,
    PayoutSerializer, PayoutListSerializer,
    AuthorLedgerSerializer,
    AuthorDashboardSerializer, BooksellertDashboardSerializer,
)
from .permissions import IsAuthor, IsStaff, IsOwnerOrStaff


# ============================================================================
# Organization & Location ViewSets
# ============================================================================

class OrganizationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for organizations.
    """
    queryset = Organization.objects.filter(is_active=True)
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "list":
            return OrganizationListSerializer
        return OrganizationSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        # Staff can only see their own organization
        if hasattr(self.request.user, "staff_profile"):
            qs = qs.filter(id=self.request.user.staff_profile.org_id)
        return qs

    @action(detail=True, methods=["get"])
    def authors(self, request, pk=None):
        """Get all authors for this organization."""
        org = self.get_object()
        memberships = AuthorOrganization.objects.filter(
            org=org, status="active"
        ).select_related("author__user")
        serializer = AuthorOrganizationSerializer(memberships, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def inventory(self, request, pk=None):
        """Get inventory for this organization."""
        org = self.get_object()
        inventory = InventorySnapshot.objects.filter(
            org=org, quantity_on_hand__gt=0
        ).select_related("book", "location")
        serializer = InventorySnapshotSerializer(inventory, many=True)
        return Response(serializer.data)


class LocationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for locations.
    """
    queryset = Location.objects.filter(is_active=True)
    serializer_class = LocationSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaff]

    def get_queryset(self):
        qs = super().get_queryset()
        # Filter to staff's organization
        if hasattr(self.request.user, "staff_profile"):
            qs = qs.filter(org=self.request.user.staff_profile.org)
        return qs

    def perform_create(self, serializer):
        # Auto-set organization from staff profile
        serializer.save(
            org=self.request.user.staff_profile.org,
            created_by=self.request.user,
        )


# ============================================================================
# Author ViewSets
# ============================================================================

class AuthorProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoint for author profiles.
    """
    queryset = AuthorProfile.objects.filter(is_active=True)
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return AuthorProfileCreateSerializer
        if self.action == "list":
            return AuthorListSerializer
        return AuthorProfileSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        # Authors can only see themselves
        if hasattr(self.request.user, "author_profile"):
            qs = qs.filter(id=self.request.user.author_profile.id)
        # Staff can see authors in their organization
        elif hasattr(self.request.user, "staff_profile"):
            org = self.request.user.staff_profile.org
            author_ids = AuthorOrganization.objects.filter(
                org=org, status="active"
            ).values_list("author_id", flat=True)
            qs = qs.filter(id__in=author_ids)
        return qs

    @action(detail=False, methods=["get"])
    def me(self, request):
        """Get current author's profile."""
        if not hasattr(request.user, "author_profile"):
            return Response(
                {"error": "You are not an author"},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = AuthorProfileSerializer(request.user.author_profile)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def dashboard(self, request):
        """Get author dashboard data."""
        if not hasattr(request.user, "author_profile"):
            return Response(
                {"error": "You are not an author"},
                status=status.HTTP_403_FORBIDDEN
            )

        author = request.user.author_profile

        # Aggregate data
        total_books = Book.objects.filter(author=author, is_active=True).count()

        consignment_data = ConsignmentItem.objects.filter(
            batch__author=author, batch__status="active"
        ).aggregate(
            on_consignment=Sum("quantity_consigned"),
            sold=Sum("quantity_sold"),
        )

        earnings_data = Sale.objects.filter(
            book__author=author
        ).aggregate(
            total_earnings=Sum("author_earnings"),
        )

        paid_data = Payout.objects.filter(
            author=author, status="completed"
        ).aggregate(
            total_paid=Sum("amount"),
        )

        total_earnings = earnings_data["total_earnings"] or Decimal("0.00")
        total_paid = paid_data["total_paid"] or Decimal("0.00")

        recent_sales = Sale.objects.filter(
            book__author=author
        ).select_related("book", "location").order_by("-sold_at")[:10]

        recent_payouts = Payout.objects.filter(
            author=author
        ).order_by("-created_at")[:5]

        data = {
            "total_books": total_books,
            "total_on_consignment": consignment_data["on_consignment"] or 0,
            "total_sold": consignment_data["sold"] or 0,
            "total_earnings": total_earnings,
            "total_paid": total_paid,
            "balance_due": total_earnings - total_paid,
            "recent_sales": SaleListSerializer(recent_sales, many=True).data,
            "recent_payouts": PayoutListSerializer(recent_payouts, many=True).data,
        }

        return Response(data)


# ============================================================================
# Book ViewSets
# ============================================================================

class BookViewSet(viewsets.ModelViewSet):
    """
    API endpoint for books.
    """
    queryset = Book.objects.filter(is_active=True)
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "list":
            return BookListSerializer
        return BookSerializer

    def get_queryset(self):
        qs = super().get_queryset().select_related("author__user")

        # Authors can only see their own books
        if hasattr(self.request.user, "author_profile"):
            qs = qs.filter(author=self.request.user.author_profile)
        # Staff can see approved books for their organization
        elif hasattr(self.request.user, "staff_profile"):
            org = self.request.user.staff_profile.org
            approved_book_ids = BookApproval.objects.filter(
                org=org, status="approved"
            ).values_list("book_id", flat=True)
            qs = qs.filter(id__in=approved_book_ids)

        # Filter by author
        author_id = self.request.query_params.get("author")
        if author_id:
            qs = qs.filter(author_id=author_id)

        # Filter by ISBN
        isbn = self.request.query_params.get("isbn")
        if isbn:
            qs = qs.filter(Q(isbn__icontains=isbn) | Q(isbn13__icontains=isbn))

        return qs

    def perform_create(self, serializer):
        # Authors can only create books for themselves
        if hasattr(self.request.user, "author_profile"):
            serializer.save(
                author=self.request.user.author_profile,
                created_by=self.request.user,
            )
        else:
            serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[IsStaff])
    def approve(self, request, pk=None):
        """Approve a book for the staff's organization."""
        book = self.get_object()
        org = request.user.staff_profile.org

        approval, created = BookApproval.objects.get_or_create(
            book=book,
            org=org,
            defaults={
                "status": "approved",
                "reviewed_at": timezone.now(),
                "reviewed_by": request.user,
            }
        )

        if not created:
            approval.status = "approved"
            approval.reviewed_at = timezone.now()
            approval.reviewed_by = request.user
            approval.save()

        serializer = BookApprovalSerializer(approval)
        return Response(serializer.data)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for book categories.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class BookApprovalViewSet(viewsets.ModelViewSet):
    """
    API endpoint for book approvals.
    """
    queryset = BookApproval.objects.all()
    serializer_class = BookApprovalSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaff]

    def get_queryset(self):
        qs = super().get_queryset()
        # Staff can only see approvals for their organization
        if hasattr(self.request.user, "staff_profile"):
            qs = qs.filter(org=self.request.user.staff_profile.org)
        return qs.select_related("book__author__user", "org")

    @action(detail=False, methods=["get"])
    def pending(self, request):
        """Get pending book approvals."""
        qs = self.get_queryset().filter(status="pending")
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


# ============================================================================
# Consignment ViewSets
# ============================================================================

class ConsignmentBatchViewSet(viewsets.ModelViewSet):
    """
    API endpoint for consignment batches.
    """
    queryset = ConsignmentBatch.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "list":
            return ConsignmentBatchListSerializer
        return ConsignmentBatchSerializer

    def get_queryset(self):
        qs = super().get_queryset().select_related(
            "author__user", "org", "location"
        ).prefetch_related("items__book")

        # Authors can see their own batches
        if hasattr(self.request.user, "author_profile"):
            qs = qs.filter(author=self.request.user.author_profile)
        # Staff can see batches for their organization
        elif hasattr(self.request.user, "staff_profile"):
            qs = qs.filter(org=self.request.user.staff_profile.org)

        return qs

    def perform_create(self, serializer):
        org = self.request.user.staff_profile.org
        serializer.save(org=org, created_by=self.request.user)

    @action(detail=True, methods=["post"])
    def add_items(self, request, pk=None):
        """Add items to a consignment batch."""
        batch = self.get_object()
        items_data = request.data.get("items", [])

        created_items = []
        for item_data in items_data:
            item_data["batch"] = batch.id
            serializer = ConsignmentItemSerializer(data=item_data)
            serializer.is_valid(raise_exception=True)
            item = serializer.save(batch=batch, created_by=request.user)
            created_items.append(item)

            # Create inventory transaction
            InventoryTransaction.objects.create(
                org=batch.org,
                location=batch.location,
                book=item.book,
                consignment_item=item,
                transaction_type="receive",
                quantity_change=item.quantity_consigned,
                quantity_after=item.quantity_consigned,  # Will be recalculated
                reference_type="ConsignmentItem",
                reference_id=item.id,
                created_by=request.user,
            )

        return Response(
            ConsignmentItemSerializer(created_items, many=True).data,
            status=status.HTTP_201_CREATED
        )


# ============================================================================
# Sales ViewSets
# ============================================================================

class SaleViewSet(viewsets.ModelViewSet):
    """
    API endpoint for sales.
    """
    queryset = Sale.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "list":
            return SaleListSerializer
        return SaleSerializer

    def get_queryset(self):
        qs = super().get_queryset().select_related(
            "book__author__user", "location", "org"
        )

        # Authors can see sales of their books
        if hasattr(self.request.user, "author_profile"):
            qs = qs.filter(book__author=self.request.user.author_profile)
        # Staff can see sales for their organization
        elif hasattr(self.request.user, "staff_profile"):
            qs = qs.filter(org=self.request.user.staff_profile.org)

        # Date filters
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")
        if start_date:
            qs = qs.filter(sold_at__date__gte=start_date)
        if end_date:
            qs = qs.filter(sold_at__date__lte=end_date)

        return qs.order_by("-sold_at")

    def perform_create(self, serializer):
        org = self.request.user.staff_profile.org

        # Get author share rate
        book = serializer.validated_data["book"]
        author_share_rate = org.default_author_share

        # Check for overrides
        try:
            author_org = AuthorOrganization.objects.get(
                author=book.author, org=org
            )
            if author_org.author_share_override:
                author_share_rate = author_org.author_share_override
        except AuthorOrganization.DoesNotExist:
            pass

        serializer.save(
            org=org,
            author_share_rate=author_share_rate,
            created_by=self.request.user,
        )


class SalesImportViewSet(viewsets.ModelViewSet):
    """
    API endpoint for sales imports.
    """
    queryset = SalesImport.objects.all()
    serializer_class = SalesImportSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaff]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        qs = super().get_queryset()
        if hasattr(self.request.user, "staff_profile"):
            qs = qs.filter(org=self.request.user.staff_profile.org)
        return qs.order_by("-created_at")

    def perform_create(self, serializer):
        org = self.request.user.staff_profile.org
        file = self.request.FILES.get("file")

        instance = serializer.save(
            org=org,
            original_filename=file.name if file else "",
            file_size=file.size if file else 0,
            created_by=self.request.user,
        )

        # Process the CSV
        self._process_csv(instance)

    def _process_csv(self, sales_import):
        """Process uploaded CSV file."""
        sales_import.status = "processing"
        sales_import.started_at = timezone.now()
        sales_import.save()

        errors = []
        success_count = 0
        row_count = 0

        try:
            file_content = sales_import.file.read().decode("utf-8")
            reader = csv.DictReader(io.StringIO(file_content))

            for row in reader:
                row_count += 1
                try:
                    isbn = row.get("isbn", "").strip()
                    quantity = int(row.get("quantity", row.get("qty", 1)))

                    # Find book by ISBN
                    book = Book.objects.filter(
                        Q(isbn=isbn) | Q(isbn13=isbn)
                    ).first()

                    if not book:
                        errors.append(f"Row {row_count}: Book with ISBN '{isbn}' not found")
                        continue

                    # Create sale
                    Sale.objects.create(
                        org=sales_import.org,
                        location=sales_import.location or sales_import.org.locations.first(),
                        book=book,
                        quantity=quantity,
                        unit_price=book.retail_price,
                        author_share_rate=sales_import.org.default_author_share,
                        sold_at=sales_import.sales_date or timezone.now(),
                        source="csv_import",
                        sales_import=sales_import,
                        created_by=sales_import.created_by,
                    )
                    success_count += 1

                except Exception as e:
                    errors.append(f"Row {row_count}: {str(e)}")

            sales_import.total_rows = row_count
            sales_import.processed_rows = row_count
            sales_import.success_count = success_count
            sales_import.error_count = len(errors)
            sales_import.error_log = "\n".join(errors)
            sales_import.status = "completed" if not errors else "partial"
            sales_import.completed_at = timezone.now()
            sales_import.save()

        except Exception as e:
            sales_import.status = "failed"
            sales_import.error_log = str(e)
            sales_import.completed_at = timezone.now()
            sales_import.save()


class InventorySnapshotViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for inventory snapshots (read-only).
    """
    queryset = InventorySnapshot.objects.all()
    serializer_class = InventorySnapshotSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset().select_related("book", "location", "org")

        if hasattr(self.request.user, "staff_profile"):
            qs = qs.filter(org=self.request.user.staff_profile.org)

        # Filter by location
        location_id = self.request.query_params.get("location")
        if location_id:
            qs = qs.filter(location_id=location_id)

        # Filter by low stock
        low_stock = self.request.query_params.get("low_stock")
        if low_stock:
            qs = qs.filter(quantity_on_hand__lte=int(low_stock))

        return qs


class InventoryTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for inventory transactions (read-only audit log).
    """
    queryset = InventoryTransaction.objects.all()
    serializer_class = InventoryTransactionSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaff]

    def get_queryset(self):
        qs = super().get_queryset().select_related("book", "location", "org")

        if hasattr(self.request.user, "staff_profile"):
            qs = qs.filter(org=self.request.user.staff_profile.org)

        return qs.order_by("-transaction_date")


# ============================================================================
# Payout ViewSets
# ============================================================================

class PaymentPeriodViewSet(viewsets.ModelViewSet):
    """
    API endpoint for payment periods.
    """
    queryset = PaymentPeriod.objects.all()
    serializer_class = PaymentPeriodSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaff]

    def get_queryset(self):
        qs = super().get_queryset()
        if hasattr(self.request.user, "staff_profile"):
            qs = qs.filter(org=self.request.user.staff_profile.org)
        return qs.order_by("-period_end")

    def perform_create(self, serializer):
        org = self.request.user.staff_profile.org
        serializer.save(org=org, created_by=self.request.user)

    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        """Close a payment period."""
        period = self.get_object()
        period.close()
        serializer = self.get_serializer(period)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def balances(self, request, pk=None):
        """Get author balances for this period."""
        period = self.get_object()
        balances = AuthorBalance.objects.filter(period=period)
        serializer = AuthorBalanceSerializer(balances, many=True)
        return Response(serializer.data)


class AuthorBalanceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for author balances.
    """
    queryset = AuthorBalance.objects.all()
    serializer_class = AuthorBalanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset().select_related(
            "author__user", "org", "period"
        )

        # Authors can see their own balances
        if hasattr(self.request.user, "author_profile"):
            qs = qs.filter(author=self.request.user.author_profile)
        # Staff can see balances for their organization
        elif hasattr(self.request.user, "staff_profile"):
            qs = qs.filter(org=self.request.user.staff_profile.org)

        return qs.order_by("-period__period_end")

    @action(detail=False, methods=["get"])
    def unpaid(self, request):
        """Get unpaid balances."""
        qs = self.get_queryset().exclude(status="paid")
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class PayoutViewSet(viewsets.ModelViewSet):
    """
    API endpoint for payouts.
    """
    queryset = Payout.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "list":
            return PayoutListSerializer
        return PayoutSerializer

    def get_queryset(self):
        qs = super().get_queryset().select_related("author__user", "org")

        # Authors can see their own payouts
        if hasattr(self.request.user, "author_profile"):
            qs = qs.filter(author=self.request.user.author_profile)
        # Staff can see payouts for their organization
        elif hasattr(self.request.user, "staff_profile"):
            qs = qs.filter(org=self.request.user.staff_profile.org)

        return qs.order_by("-created_at")

    def perform_create(self, serializer):
        org = self.request.user.staff_profile.org
        serializer.save(org=org, created_by=self.request.user)

    @action(detail=True, methods=["post"])
    def mark_paid(self, request, pk=None):
        """Mark a payout as paid."""
        payout = self.get_object()
        reference = request.data.get("reference", "")
        payout.mark_paid(reference=reference)
        serializer = self.get_serializer(payout)
        return Response(serializer.data)


class AuthorLedgerViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for author ledger entries (read-only audit log).
    """
    queryset = AuthorLedger.objects.all()
    serializer_class = AuthorLedgerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset().select_related("author__user", "org")

        # Authors can see their own ledger
        if hasattr(self.request.user, "author_profile"):
            qs = qs.filter(author=self.request.user.author_profile)
        # Staff can see ledgers for their organization
        elif hasattr(self.request.user, "staff_profile"):
            qs = qs.filter(org=self.request.user.staff_profile.org)

        return qs.order_by("-entry_date")


# ============================================================================
# Dashboard ViewSets
# ============================================================================

class StaffDashboardViewSet(viewsets.ViewSet):
    """
    API endpoint for staff dashboard.
    """
    permission_classes = [permissions.IsAuthenticated, IsStaff]

    def list(self, request):
        """Get bookseller dashboard data."""
        org = request.user.staff_profile.org

        # Get current period
        today = timezone.now().date()
        current_period = PaymentPeriod.objects.filter(
            org=org,
            period_start__lte=today,
            period_end__gte=today,
        ).first()

        # Aggregate data
        total_authors = AuthorOrganization.objects.filter(
            org=org, status="active"
        ).count()

        total_books = BookApproval.objects.filter(
            org=org, status="approved"
        ).count()

        total_inventory = InventorySnapshot.objects.filter(
            org=org
        ).aggregate(total=Sum("quantity_on_hand"))["total"] or 0

        # Period sales
        if current_period:
            period_data = Sale.objects.filter(
                org=org,
                sold_at__date__gte=current_period.period_start,
                sold_at__date__lte=current_period.period_end,
            ).aggregate(
                total_sales=Sum(F("unit_price") * F("quantity")),
                author_earnings=Sum("author_earnings"),
            )
            period_sales = period_data["total_sales"] or Decimal("0.00")
            period_author_earnings = period_data["author_earnings"] or Decimal("0.00")
        else:
            period_sales = Decimal("0.00")
            period_author_earnings = Decimal("0.00")

        # Pending payouts
        pending_payouts = AuthorBalance.objects.filter(
            org=org
        ).exclude(status="paid").aggregate(
            total=Sum(F("earnings_total") - F("amount_paid"))
        )["total"] or Decimal("0.00")

        # Recent sales
        recent_sales = Sale.objects.filter(
            org=org
        ).select_related("book", "location").order_by("-sold_at")[:10]

        # Low stock items
        low_stock_items = InventorySnapshot.objects.filter(
            org=org,
            quantity_on_hand__lte=5,
            quantity_on_hand__gt=0,
        ).select_related("book", "location")[:10]

        data = {
            "total_authors": total_authors,
            "total_books": total_books,
            "total_inventory": total_inventory,
            "period_sales": period_sales,
            "period_author_earnings": period_author_earnings,
            "period_store_earnings": period_sales - period_author_earnings,
            "pending_payouts": pending_payouts,
            "recent_sales": SaleListSerializer(recent_sales, many=True).data,
            "low_stock_items": InventorySnapshotSerializer(low_stock_items, many=True).data,
        }

        return Response(data)
