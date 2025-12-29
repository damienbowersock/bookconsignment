from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal

from accounts.models import AuditedModel, AuthorProfile, Organization


class PaymentPeriod(AuditedModel):
    """
    Represents a payment period for an organization.
    Aggregates sales and calculates author earnings for a time period.
    """
    org = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="payment_periods",
    )

    # Period dates
    period_start = models.DateField()
    period_end = models.DateField()
    name = models.CharField(
        max_length=100,
        blank=True,
        help_text="e.g., 'January 2025', 'Week 1 2025'",
    )

    STATUS_CHOICES = [
        ("open", "Open"),
        ("closed", "Closed"),
        ("processing", "Processing Payments"),
        ("completed", "Completed"),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="open",
    )

    # Aggregates (calculated)
    total_sales = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    total_author_earnings = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    total_store_earnings = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    closed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-period_end"]
        unique_together = [["org", "period_start", "period_end"]]
        verbose_name = "Payment Period"
        verbose_name_plural = "Payment Periods"

    def __str__(self):
        return f"{self.org.name}: {self.name or f'{self.period_start} to {self.period_end}'}"

    def calculate_totals(self):
        """Recalculate totals from sales in this period."""
        from sales.models import Sale
        from django.db.models import Sum

        sales = Sale.objects.filter(
            org=self.org,
            sold_at__date__gte=self.period_start,
            sold_at__date__lte=self.period_end,
        )

        totals = sales.aggregate(
            total_sales=Sum("net_amount"),
            total_author=Sum("author_earnings"),
        )

        self.total_sales = totals["total_sales"] or Decimal("0.00")
        self.total_author_earnings = totals["total_author"] or Decimal("0.00")
        self.total_store_earnings = self.total_sales - self.total_author_earnings
        self.save()

    def close(self):
        """Close the period and generate author balances."""
        self.status = "closed"
        self.closed_at = timezone.now()
        self.calculate_totals()
        self.save()

        # Generate author balance records
        self._generate_author_balances()

    def _generate_author_balances(self):
        """Generate AuthorBalance records for this period."""
        from sales.models import Sale
        from django.db.models import Sum

        # Get sales grouped by author
        author_sales = (
            Sale.objects.filter(
                org=self.org,
                sold_at__date__gte=self.period_start,
                sold_at__date__lte=self.period_end,
            )
            .values("book__author")
            .annotate(
                total_sales=Sum("net_amount"),
                total_earnings=Sum("author_earnings"),
            )
        )

        for author_data in author_sales:
            author_id = author_data["book__author"]
            if author_id:
                AuthorBalance.objects.update_or_create(
                    author_id=author_id,
                    org=self.org,
                    period=self,
                    defaults={
                        "sales_total": author_data["total_sales"] or Decimal("0.00"),
                        "earnings_total": author_data["total_earnings"] or Decimal("0.00"),
                    }
                )


class AuthorBalance(AuditedModel):
    """
    Tracks an author's earnings balance for a specific period and organization.
    """
    author = models.ForeignKey(
        AuthorProfile,
        on_delete=models.CASCADE,
        related_name="balances",
    )
    org = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="author_balances",
    )
    period = models.ForeignKey(
        PaymentPeriod,
        on_delete=models.CASCADE,
        related_name="author_balances",
    )

    # Earnings for this period
    sales_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Total sales amount for this period",
    )
    earnings_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Author's earnings for this period",
    )

    # Payment tracking
    amount_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("partial", "Partially Paid"),
        ("paid", "Fully Paid"),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )

    class Meta:
        ordering = ["-period__period_end"]
        unique_together = [["author", "org", "period"]]
        verbose_name = "Author Balance"
        verbose_name_plural = "Author Balances"

    def __str__(self):
        return f"{self.author} - {self.period}: ${self.balance_due}"

    @property
    def balance_due(self):
        """Amount still owed to author."""
        return self.earnings_total - self.amount_paid

    def update_status(self):
        """Update status based on payment amount."""
        if self.amount_paid >= self.earnings_total:
            self.status = "paid"
        elif self.amount_paid > 0:
            self.status = "partial"
        else:
            self.status = "pending"
        self.save()


class Payout(AuditedModel):
    """
    A payment made to an author.
    """
    author = models.ForeignKey(
        AuthorProfile,
        on_delete=models.PROTECT,
        related_name="payouts",
    )
    org = models.ForeignKey(
        Organization,
        on_delete=models.PROTECT,
        related_name="payouts",
    )

    # Payment amount
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )

    # Payment method
    METHOD_CHOICES = [
        ("venmo", "Venmo"),
        ("paypal", "PayPal"),
        ("ach", "ACH Bank Transfer"),
        ("check", "Check"),
        ("cash", "Cash"),
        ("other", "Other"),
    ]
    method = models.CharField(
        max_length=20,
        choices=METHOD_CHOICES,
        default="venmo",
    )

    # Reference/tracking
    reference = models.CharField(
        max_length=255,
        blank=True,
        help_text="Transaction ID, check number, Venmo note, etc.",
    )

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("cancelled", "Cancelled"),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )

    # Timestamps
    scheduled_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When payment is scheduled to be sent",
    )
    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When payment was actually sent",
    )
    confirmed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When payment was confirmed received",
    )

    notes = models.TextField(blank=True)

    # Integration fields (for future Venmo/PayPal API)
    external_id = models.CharField(
        max_length=255,
        blank=True,
        help_text="External payment system transaction ID",
    )
    external_status = models.CharField(
        max_length=50,
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Payout"
        verbose_name_plural = "Payouts"

    def __str__(self):
        return f"${self.amount} to {self.author} ({self.get_status_display()})"

    def mark_paid(self, reference=None):
        """Mark payout as completed."""
        self.status = "completed"
        self.paid_at = timezone.now()
        if reference:
            self.reference = reference
        self.save()

        # Update linked balance records
        for item in self.line_items.all():
            if item.balance:
                item.balance.amount_paid += item.amount
                item.balance.update_status()


class PayoutLineItem(AuditedModel):
    """
    Individual line items in a payout.
    Links payouts to specific author balances (periods).
    """
    payout = models.ForeignKey(
        Payout,
        on_delete=models.CASCADE,
        related_name="line_items",
    )
    balance = models.ForeignKey(
        AuthorBalance,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payout_items",
    )

    # Amount from this balance being paid
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )

    # Description
    description = models.CharField(
        max_length=255,
        blank=True,
        help_text="e.g., 'January 2025 sales'",
    )

    class Meta:
        ordering = ["id"]
        verbose_name = "Payout Line Item"
        verbose_name_plural = "Payout Line Items"

    def __str__(self):
        return f"${self.amount} - {self.description or self.balance}"


class AuthorLedger(AuditedModel):
    """
    Complete ledger of all financial transactions for an author.
    Provides a full audit trail of earnings and payments.
    """
    author = models.ForeignKey(
        AuthorProfile,
        on_delete=models.CASCADE,
        related_name="ledger_entries",
    )
    org = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="author_ledger_entries",
    )

    ENTRY_TYPE_CHOICES = [
        ("sale", "Sale Earnings"),
        ("adjustment_credit", "Adjustment (Credit)"),
        ("adjustment_debit", "Adjustment (Debit)"),
        ("payout", "Payout"),
        ("return_debit", "Return (Debit)"),
    ]
    entry_type = models.CharField(
        max_length=20,
        choices=ENTRY_TYPE_CHOICES,
    )

    # Amount (positive = credit, negative = debit)
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    # Running balance after this entry
    balance_after = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    # Reference to source record
    reference_type = models.CharField(
        max_length=50,
        blank=True,
    )
    reference_id = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    description = models.CharField(max_length=255, blank=True)
    entry_date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-entry_date", "-created_at"]
        indexes = [
            models.Index(fields=["author", "org"]),
            models.Index(fields=["entry_date"]),
        ]
        verbose_name = "Author Ledger Entry"
        verbose_name_plural = "Author Ledger Entries"

    def __str__(self):
        return f"{self.author}: {self.get_entry_type_display()} ${self.amount}"

    @classmethod
    def get_current_balance(cls, author, org):
        """Get current balance for an author at an organization."""
        last_entry = cls.objects.filter(
            author=author,
            org=org,
        ).order_by("-entry_date", "-created_at").first()

        if last_entry:
            return last_entry.balance_after
        return Decimal("0.00")

    @classmethod
    def create_entry(cls, author, org, entry_type, amount, description="", reference_type="", reference_id=None):
        """Create a new ledger entry with calculated balance."""
        current_balance = cls.get_current_balance(author, org)
        new_balance = current_balance + amount

        return cls.objects.create(
            author=author,
            org=org,
            entry_type=entry_type,
            amount=amount,
            balance_after=new_balance,
            description=description,
            reference_type=reference_type,
            reference_id=reference_id,
        )
