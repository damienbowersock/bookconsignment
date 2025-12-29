from rest_framework import serializers
from django.contrib.auth.models import User

from accounts.models import (
    Organization, Location, AuthorProfile, StaffProfile, AuthorOrganization
)
from catalog.models import Book, Category, BookApproval
from consignment.models import (
    ConsignmentBatch, ConsignmentItem, ConsignmentReturn, ConsignmentReturnItem
)
from sales.models import Sale, SalesImport, InventoryTransaction, InventorySnapshot
from payouts.models import (
    PaymentPeriod, AuthorBalance, Payout, PayoutLineItem, AuthorLedger
)


# ============================================================================
# User Serializers
# ============================================================================

class UserSerializer(serializers.ModelSerializer):
    """Basic user serializer."""
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "full_name"]
        read_only_fields = ["id", "username"]

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new users."""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "password_confirm", "first_name", "last_name"]

    def validate(self, data):
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match"})
        return data

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


# ============================================================================
# Organization & Location Serializers
# ============================================================================

class LocationSerializer(serializers.ModelSerializer):
    """Location serializer."""
    class Meta:
        model = Location
        fields = [
            "id", "name", "address_line1", "address_line2", "city", "state",
            "postal_code", "country", "phone", "email", "external_id", "is_active",
            "created_at", "updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class OrganizationSerializer(serializers.ModelSerializer):
    """Organization serializer."""
    locations = LocationSerializer(many=True, read_only=True)
    location_count = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = [
            "id", "name", "slug", "email", "phone", "website",
            "address_line1", "address_line2", "city", "state", "postal_code", "country",
            "default_author_share", "default_consignment_period_days",
            "payment_cycle", "minimum_payout_amount", "is_active",
            "locations", "location_count", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "slug", "created_at", "updated_at"]

    def get_location_count(self, obj):
        return obj.locations.count()


class OrganizationListSerializer(serializers.ModelSerializer):
    """Compact organization serializer for lists."""
    location_count = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = ["id", "name", "slug", "city", "state", "is_active", "location_count"]

    def get_location_count(self, obj):
        return obj.locations.count()


# ============================================================================
# Author Serializers
# ============================================================================

class AuthorProfileSerializer(serializers.ModelSerializer):
    """Full author profile serializer."""
    user = UserSerializer(read_only=True)
    full_name = serializers.CharField(source="user.get_full_name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = AuthorProfile
        fields = [
            "id", "user", "full_name", "email", "phone", "website",
            "address_line1", "address_line2", "city", "state", "postal_code", "country",
            "preferred_payment_method", "payment_handle", "bio", "is_active",
            "created_at", "updated_at"
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at"]


class AuthorProfileCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating author profiles."""
    user = UserCreateSerializer()

    class Meta:
        model = AuthorProfile
        fields = [
            "user", "phone", "website",
            "address_line1", "address_line2", "city", "state", "postal_code", "country",
            "preferred_payment_method", "payment_handle", "bio"
        ]

    def create(self, validated_data):
        user_data = validated_data.pop("user")
        user_serializer = UserCreateSerializer(data=user_data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()

        # Add to Authors group
        from django.contrib.auth.models import Group
        authors_group, _ = Group.objects.get_or_create(name="Authors")
        user.groups.add(authors_group)

        return AuthorProfile.objects.create(user=user, **validated_data)


class AuthorListSerializer(serializers.ModelSerializer):
    """Compact author serializer for lists."""
    full_name = serializers.CharField(source="user.get_full_name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = AuthorProfile
        fields = ["id", "full_name", "email", "phone", "is_active"]


# ============================================================================
# Staff Serializers
# ============================================================================

class StaffProfileSerializer(serializers.ModelSerializer):
    """Staff profile serializer."""
    user = UserSerializer(read_only=True)
    org = OrganizationListSerializer(read_only=True)
    full_name = serializers.CharField(source="user.get_full_name", read_only=True)

    class Meta:
        model = StaffProfile
        fields = [
            "id", "user", "org", "full_name", "role", "phone", "is_active",
            "created_at", "updated_at"
        ]
        read_only_fields = ["id", "user", "org", "created_at", "updated_at"]


# ============================================================================
# Author-Organization Relationship Serializers
# ============================================================================

class AuthorOrganizationSerializer(serializers.ModelSerializer):
    """Author-Organization relationship serializer."""
    author = AuthorListSerializer(read_only=True)
    org = OrganizationListSerializer(read_only=True)
    effective_author_share = serializers.DecimalField(
        max_digits=5, decimal_places=4, read_only=True
    )

    class Meta:
        model = AuthorOrganization
        fields = [
            "id", "author", "org", "status",
            "author_share_override", "consignment_period_days_override",
            "effective_author_share", "joined_at", "notes",
            "created_at", "updated_at"
        ]
        read_only_fields = ["id", "joined_at", "created_at", "updated_at"]


# ============================================================================
# Catalog Serializers
# ============================================================================

class CategorySerializer(serializers.ModelSerializer):
    """Category serializer."""
    class Meta:
        model = Category
        fields = ["id", "name", "slug", "parent", "description"]


class BookSerializer(serializers.ModelSerializer):
    """Full book serializer."""
    author = AuthorListSerializer(read_only=True)
    author_id = serializers.PrimaryKeyRelatedField(
        queryset=AuthorProfile.objects.all(),
        source="author",
        write_only=True
    )
    categories = CategorySerializer(many=True, read_only=True)
    category_ids = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source="categories",
        many=True,
        write_only=True,
        required=False
    )
    display_isbn = serializers.CharField(read_only=True)
    cover_url = serializers.CharField(read_only=True)

    class Meta:
        model = Book
        fields = [
            "id", "author", "author_id", "title", "subtitle", "description",
            "isbn", "isbn13", "sku", "retail_price", "wholesale_price",
            "format", "page_count", "dimensions", "weight_oz",
            "cover_image", "cover_image_url", "cover_url",
            "publisher", "publication_date", "edition", "language",
            "categories", "category_ids", "display_isbn", "is_active",
            "created_at", "updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class BookListSerializer(serializers.ModelSerializer):
    """Compact book serializer for lists."""
    author_name = serializers.CharField(source="author.full_name", read_only=True)
    display_isbn = serializers.CharField(read_only=True)

    class Meta:
        model = Book
        fields = [
            "id", "title", "author_name", "display_isbn",
            "retail_price", "format", "is_active"
        ]


class BookApprovalSerializer(serializers.ModelSerializer):
    """Book approval serializer."""
    book = BookListSerializer(read_only=True)
    org = OrganizationListSerializer(read_only=True)

    class Meta:
        model = BookApproval
        fields = [
            "id", "book", "org", "status",
            "reviewed_at", "reviewed_by", "rejection_reason", "notes",
            "org_retail_price_override", "author_share_override",
            "created_at", "updated_at"
        ]
        read_only_fields = ["id", "reviewed_at", "reviewed_by", "created_at", "updated_at"]


# ============================================================================
# Consignment Serializers
# ============================================================================

class ConsignmentItemSerializer(serializers.ModelSerializer):
    """Consignment item serializer."""
    book = BookListSerializer(read_only=True)
    book_id = serializers.PrimaryKeyRelatedField(
        queryset=Book.objects.all(),
        source="book",
        write_only=True
    )
    quantity_on_hand = serializers.IntegerField(read_only=True)
    effective_unit_price = serializers.DecimalField(
        max_digits=8, decimal_places=2, read_only=True
    )

    class Meta:
        model = ConsignmentItem
        fields = [
            "id", "book", "book_id",
            "quantity_consigned", "quantity_sold", "quantity_returned", "quantity_damaged",
            "quantity_on_hand", "author_share_override", "unit_price_override",
            "effective_unit_price", "notes", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "quantity_sold", "quantity_returned", "quantity_damaged", "created_at", "updated_at"]


class ConsignmentBatchSerializer(serializers.ModelSerializer):
    """Consignment batch serializer."""
    author = AuthorListSerializer(read_only=True)
    author_id = serializers.PrimaryKeyRelatedField(
        queryset=AuthorProfile.objects.all(),
        source="author",
        write_only=True
    )
    org = OrganizationListSerializer(read_only=True)
    location = LocationSerializer(read_only=True)
    location_id = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(),
        source="location",
        write_only=True
    )
    items = ConsignmentItemSerializer(many=True, read_only=True)
    is_expired = serializers.BooleanField(read_only=True)

    class Meta:
        model = ConsignmentBatch
        fields = [
            "id", "author", "author_id", "org", "location", "location_id",
            "batch_number", "received_date", "notes",
            "consignment_period_days", "consignment_end_date", "status",
            "is_expired", "items", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "org", "consignment_end_date", "created_at", "updated_at"]


class ConsignmentBatchListSerializer(serializers.ModelSerializer):
    """Compact consignment batch serializer for lists."""
    author_name = serializers.CharField(source="author.full_name", read_only=True)
    location_name = serializers.CharField(source="location.name", read_only=True)
    item_count = serializers.SerializerMethodField()

    class Meta:
        model = ConsignmentBatch
        fields = [
            "id", "author_name", "location_name", "batch_number",
            "received_date", "status", "item_count"
        ]

    def get_item_count(self, obj):
        return obj.items.count()


# ============================================================================
# Sales Serializers
# ============================================================================

class SaleSerializer(serializers.ModelSerializer):
    """Sale serializer."""
    book = BookListSerializer(read_only=True)
    book_id = serializers.PrimaryKeyRelatedField(
        queryset=Book.objects.all(),
        source="book",
        write_only=True
    )
    location = LocationSerializer(read_only=True)
    location_id = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(),
        source="location",
        write_only=True
    )
    gross_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    net_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Sale
        fields = [
            "id", "org", "book", "book_id", "location", "location_id",
            "consignment_item", "quantity", "unit_price",
            "discount_amount", "tax_amount",
            "gross_amount", "net_amount", "total_amount",
            "author_share_rate", "author_earnings",
            "sold_at", "source", "external_id", "sales_import", "notes",
            "created_at", "updated_at"
        ]
        read_only_fields = [
            "id", "org", "author_earnings", "created_at", "updated_at"
        ]


class SaleListSerializer(serializers.ModelSerializer):
    """Compact sale serializer for lists."""
    book_title = serializers.CharField(source="book.title", read_only=True)
    location_name = serializers.CharField(source="location.name", read_only=True)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Sale
        fields = [
            "id", "book_title", "location_name", "quantity",
            "unit_price", "total_amount", "sold_at", "source"
        ]


class SalesImportSerializer(serializers.ModelSerializer):
    """Sales import serializer."""
    class Meta:
        model = SalesImport
        fields = [
            "id", "org", "location", "file", "original_filename", "file_size",
            "status", "total_rows", "processed_rows", "success_count", "error_count",
            "error_log", "started_at", "completed_at", "sales_date", "source",
            "created_at", "updated_at"
        ]
        read_only_fields = [
            "id", "org", "file_size", "status", "total_rows", "processed_rows",
            "success_count", "error_count", "error_log", "started_at", "completed_at",
            "created_at", "updated_at"
        ]


class InventorySnapshotSerializer(serializers.ModelSerializer):
    """Inventory snapshot serializer."""
    book = BookListSerializer(read_only=True)
    location = LocationSerializer(read_only=True)

    class Meta:
        model = InventorySnapshot
        fields = [
            "id", "org", "location", "book",
            "quantity_on_hand", "quantity_reserved", "quantity_available",
            "total_received", "total_sold", "total_returned_author", "total_damaged",
            "last_received_at", "last_sold_at", "updated_at"
        ]


class InventoryTransactionSerializer(serializers.ModelSerializer):
    """Inventory transaction serializer."""
    book = BookListSerializer(read_only=True)
    location = LocationSerializer(read_only=True)
    transaction_type_display = serializers.CharField(
        source="get_transaction_type_display", read_only=True
    )

    class Meta:
        model = InventoryTransaction
        fields = [
            "id", "org", "location", "book", "consignment_item",
            "transaction_type", "transaction_type_display",
            "quantity_change", "quantity_after",
            "reference_type", "reference_id", "notes", "transaction_date",
            "created_at"
        ]


# ============================================================================
# Payout Serializers
# ============================================================================

class PaymentPeriodSerializer(serializers.ModelSerializer):
    """Payment period serializer."""
    org = OrganizationListSerializer(read_only=True)

    class Meta:
        model = PaymentPeriod
        fields = [
            "id", "org", "period_start", "period_end", "name", "status",
            "total_sales", "total_author_earnings", "total_store_earnings",
            "closed_at", "notes", "created_at", "updated_at"
        ]
        read_only_fields = [
            "id", "org", "total_sales", "total_author_earnings",
            "total_store_earnings", "closed_at", "created_at", "updated_at"
        ]


class AuthorBalanceSerializer(serializers.ModelSerializer):
    """Author balance serializer."""
    author = AuthorListSerializer(read_only=True)
    period = PaymentPeriodSerializer(read_only=True)
    balance_due = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = AuthorBalance
        fields = [
            "id", "author", "org", "period",
            "sales_total", "earnings_total", "amount_paid", "balance_due", "status",
            "created_at", "updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class PayoutLineItemSerializer(serializers.ModelSerializer):
    """Payout line item serializer."""
    balance = AuthorBalanceSerializer(read_only=True)

    class Meta:
        model = PayoutLineItem
        fields = ["id", "balance", "amount", "description"]


class PayoutSerializer(serializers.ModelSerializer):
    """Payout serializer."""
    author = AuthorListSerializer(read_only=True)
    author_id = serializers.PrimaryKeyRelatedField(
        queryset=AuthorProfile.objects.all(),
        source="author",
        write_only=True
    )
    org = OrganizationListSerializer(read_only=True)
    line_items = PayoutLineItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    method_display = serializers.CharField(source="get_method_display", read_only=True)

    class Meta:
        model = Payout
        fields = [
            "id", "author", "author_id", "org", "amount",
            "method", "method_display", "reference",
            "status", "status_display",
            "scheduled_at", "paid_at", "confirmed_at",
            "notes", "external_id", "external_status",
            "line_items", "created_at", "updated_at"
        ]
        read_only_fields = [
            "id", "org", "paid_at", "confirmed_at",
            "external_id", "external_status", "created_at", "updated_at"
        ]


class PayoutListSerializer(serializers.ModelSerializer):
    """Compact payout serializer for lists."""
    author_name = serializers.CharField(source="author.full_name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Payout
        fields = [
            "id", "author_name", "amount", "method", "status", "status_display",
            "paid_at", "created_at"
        ]


class AuthorLedgerSerializer(serializers.ModelSerializer):
    """Author ledger entry serializer."""
    entry_type_display = serializers.CharField(source="get_entry_type_display", read_only=True)

    class Meta:
        model = AuthorLedger
        fields = [
            "id", "author", "org", "entry_type", "entry_type_display",
            "amount", "balance_after", "reference_type", "reference_id",
            "description", "entry_date", "created_at"
        ]


# ============================================================================
# Dashboard Serializers
# ============================================================================

class AuthorDashboardSerializer(serializers.Serializer):
    """Serializer for author dashboard data."""
    total_books = serializers.IntegerField()
    total_on_consignment = serializers.IntegerField()
    total_sold = serializers.IntegerField()
    total_earnings = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_paid = serializers.DecimalField(max_digits=12, decimal_places=2)
    balance_due = serializers.DecimalField(max_digits=12, decimal_places=2)
    recent_sales = SaleListSerializer(many=True)
    recent_payouts = PayoutListSerializer(many=True)


class BooksellertDashboardSerializer(serializers.Serializer):
    """Serializer for bookseller dashboard data."""
    total_authors = serializers.IntegerField()
    total_books = serializers.IntegerField()
    total_inventory = serializers.IntegerField()
    period_sales = serializers.DecimalField(max_digits=12, decimal_places=2)
    period_author_earnings = serializers.DecimalField(max_digits=12, decimal_places=2)
    period_store_earnings = serializers.DecimalField(max_digits=12, decimal_places=2)
    pending_payouts = serializers.DecimalField(max_digits=12, decimal_places=2)
    recent_sales = SaleListSerializer(many=True)
    low_stock_items = InventorySnapshotSerializer(many=True)
