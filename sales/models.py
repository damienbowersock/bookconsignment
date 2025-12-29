import uuid
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal

from accounts.models import AuditedModel, Location, Organization, AuthorProfile
from catalog.models import Book
from consignment.models import ConsignmentItem


def csv_upload_path(instance, filename):
    """Generate upload path for CSV files."""
    ext = filename.split(".")[-1] if "." in filename else "csv"
    return f"uploads/sales/{instance.org.id}/{uuid.uuid4()}.{ext}"


class SalesImport(AuditedModel):
    """
    Record of a CSV file upload for bulk sales import.
    """
    org = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="sales_imports",
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sales_imports",
        help_text="Default location for imported sales",
    )

    # File info
    file = models.FileField(upload_to=csv_upload_path)
    original_filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(default=0)

    # Import status
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("partial", "Partially Completed"),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )

    # Results
    total_rows = models.PositiveIntegerField(default=0)
    processed_rows = models.PositiveIntegerField(default=0)
    success_count = models.PositiveIntegerField(default=0)
    error_count = models.PositiveIntegerField(default=0)
    error_log = models.TextField(blank=True)

    # Timestamps
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Date range for imported sales
    sales_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date to assign to imported sales (defaults to today)",
    )

    SOURCE_CHOICES = [
        ("manual_csv", "Manual CSV Upload"),
        ("shopify", "Shopify"),
        ("square", "Square"),
        ("other", "Other"),
    ]
    source = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES,
        default="manual_csv",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Sales Import"
        verbose_name_plural = "Sales Imports"

    def __str__(self):
        return f"{self.original_filename} ({self.status})"


class Sale(AuditedModel):
    """
    Record of a book sale.
    """
    org = models.ForeignKey(
        Organization,
        on_delete=models.PROTECT,
        related_name="sales",
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name="sales",
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.PROTECT,
        related_name="sales",
    )
    consignment_item = models.ForeignKey(
        ConsignmentItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sales",
        help_text="Link to specific consignment item (for inventory tracking)",
    )

    # Sale details
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
    )
    unit_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    discount_amount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    tax_amount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    # Consignment share at time of sale (captured for historical accuracy)
    author_share_rate = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        help_text="Author's share rate at time of sale",
    )
    author_earnings = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text="Calculated author earnings from this sale",
    )

    # Timestamps
    sold_at = models.DateTimeField(default=timezone.now)

    # Source tracking
    SOURCE_CHOICES = [
        ("manual", "Manual Entry"),
        ("csv_import", "CSV Import"),
        ("shopify", "Shopify"),
        ("square", "Square"),
        ("pos", "Point of Sale"),
        ("other", "Other"),
    ]
    source = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES,
        default="manual",
    )
    external_id = models.CharField(
        max_length=255,
        blank=True,
        help_text="External reference (order ID, transaction ID, etc.)",
    )
    sales_import = models.ForeignKey(
        SalesImport,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sales",
    )

    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-sold_at"]
        indexes = [
            models.Index(fields=["sold_at"]),
            models.Index(fields=["book", "sold_at"]),
            models.Index(fields=["org", "sold_at"]),
        ]

    def __str__(self):
        return f"Sale: {self.quantity}x {self.book.title} @ {self.location}"

    @property
    def gross_amount(self):
        """Total sale amount before discount."""
        return self.unit_price * self.quantity

    @property
    def net_amount(self):
        """Net sale amount after discount, before tax."""
        return self.gross_amount - self.discount_amount

    @property
    def total_amount(self):
        """Total amount including tax."""
        return self.net_amount + self.tax_amount

    def calculate_author_earnings(self):
        """Calculate author earnings based on net amount and share rate."""
        return self.net_amount * self.author_share_rate

    def save(self, *args, **kwargs):
        # Auto-calculate author earnings if not set
        if not self.author_earnings:
            self.author_earnings = self.calculate_author_earnings()
        super().save(*args, **kwargs)


class InventoryTransaction(AuditedModel):
    """
    Audit trail for all inventory changes.
    """
    org = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="inventory_transactions",
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name="inventory_transactions",
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.PROTECT,
        related_name="inventory_transactions",
    )
    consignment_item = models.ForeignKey(
        ConsignmentItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="inventory_transactions",
    )

    # Transaction type
    TRANSACTION_TYPE_CHOICES = [
        ("receive", "Received from Author"),
        ("sale", "Sold"),
        ("return_author", "Returned to Author"),
        ("return_customer", "Customer Return"),
        ("adjustment_add", "Adjustment (Add)"),
        ("adjustment_remove", "Adjustment (Remove)"),
        ("transfer_in", "Transfer In"),
        ("transfer_out", "Transfer Out"),
        ("damaged", "Damaged/Lost"),
    ]
    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPE_CHOICES,
    )

    # Quantity change (positive for add, negative for remove)
    quantity_change = models.IntegerField()

    # Running balance after this transaction
    quantity_after = models.PositiveIntegerField()

    # Reference to source record
    reference_type = models.CharField(
        max_length=50,
        blank=True,
        help_text="Model name of the source record",
    )
    reference_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="ID of the source record",
    )

    notes = models.TextField(blank=True)
    transaction_date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-transaction_date", "-created_at"]
        indexes = [
            models.Index(fields=["book", "location"]),
            models.Index(fields=["transaction_date"]),
        ]
        verbose_name = "Inventory Transaction"
        verbose_name_plural = "Inventory Transactions"

    def __str__(self):
        direction = "+" if self.quantity_change > 0 else ""
        return f"{self.book.title}: {direction}{self.quantity_change} ({self.get_transaction_type_display()})"


class InventorySnapshot(AuditedModel):
    """
    Current inventory levels by book and location.
    Denormalized for quick access; updated by signals/triggers.
    """
    org = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="inventory_snapshots",
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name="inventory_snapshots",
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="inventory_snapshots",
    )

    quantity_on_hand = models.PositiveIntegerField(default=0)
    quantity_reserved = models.PositiveIntegerField(
        default=0,
        help_text="Reserved for pending orders",
    )
    quantity_available = models.PositiveIntegerField(default=0)

    # Aggregates
    total_received = models.PositiveIntegerField(default=0)
    total_sold = models.PositiveIntegerField(default=0)
    total_returned_author = models.PositiveIntegerField(default=0)
    total_damaged = models.PositiveIntegerField(default=0)

    last_received_at = models.DateTimeField(null=True, blank=True)
    last_sold_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = [["org", "location", "book"]]
        ordering = ["book__title"]
        verbose_name = "Inventory Snapshot"
        verbose_name_plural = "Inventory Snapshots"

    def __str__(self):
        return f"{self.book.title} @ {self.location}: {self.quantity_on_hand} on hand"

    def recalculate(self):
        """Recalculate inventory from transactions."""
        from django.db.models import Sum

        transactions = InventoryTransaction.objects.filter(
            book=self.book,
            location=self.location,
        )

        # Calculate totals by type
        received = transactions.filter(
            transaction_type="receive"
        ).aggregate(total=Sum("quantity_change"))["total"] or 0

        sold = abs(transactions.filter(
            transaction_type="sale"
        ).aggregate(total=Sum("quantity_change"))["total"] or 0)

        returned_author = abs(transactions.filter(
            transaction_type="return_author"
        ).aggregate(total=Sum("quantity_change"))["total"] or 0)

        damaged = abs(transactions.filter(
            transaction_type="damaged"
        ).aggregate(total=Sum("quantity_change"))["total"] or 0)

        # Net change
        net_change = transactions.aggregate(
            total=Sum("quantity_change")
        )["total"] or 0

        self.quantity_on_hand = max(0, net_change)
        self.quantity_available = max(0, self.quantity_on_hand - self.quantity_reserved)
        self.total_received = received
        self.total_sold = sold
        self.total_returned_author = returned_author
        self.total_damaged = damaged

        # Get last transaction dates
        last_receive = transactions.filter(
            transaction_type="receive"
        ).order_by("-transaction_date").first()
        if last_receive:
            self.last_received_at = last_receive.transaction_date

        last_sale = transactions.filter(
            transaction_type="sale"
        ).order_by("-transaction_date").first()
        if last_sale:
            self.last_sold_at = last_sale.transaction_date

        self.save()
