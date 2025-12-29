from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal

from accounts.models import AuditedModel, AuthorProfile, Organization, Location, AuthorOrganization
from catalog.models import Book, BookApproval


class ConsignmentBatch(AuditedModel):
    """
    A batch of books delivered by an author to a bookseller.
    Tracks when inventory was received and any terms specific to this batch.
    """
    author = models.ForeignKey(
        AuthorProfile,
        on_delete=models.PROTECT,
        related_name="consignment_batches",
    )
    org = models.ForeignKey(
        Organization,
        on_delete=models.PROTECT,
        related_name="consignment_batches",
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name="consignment_batches",
    )

    # Batch info
    batch_number = models.CharField(
        max_length=50,
        blank=True,
        help_text="Optional batch/delivery reference number",
    )
    received_date = models.DateField(default=timezone.now)
    notes = models.TextField(blank=True)

    # Consignment period for this batch (overrides org/author defaults)
    consignment_period_days = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Consignment period for this batch. Leave blank to use defaults.",
    )
    consignment_end_date = models.DateField(
        null=True,
        blank=True,
        help_text="Calculated end date for consignment period",
    )

    STATUS_CHOICES = [
        ("active", "Active"),
        ("returned", "Returned to Author"),
        ("closed", "Closed"),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active",
    )

    class Meta:
        ordering = ["-received_date", "-created_at"]
        verbose_name = "Consignment Batch"
        verbose_name_plural = "Consignment Batches"

    def __str__(self):
        return f"Batch {self.batch_number or self.id} - {self.author} @ {self.location}"

    def save(self, *args, **kwargs):
        # Calculate consignment end date if period is set
        if self.consignment_period_days and not self.consignment_end_date:
            from datetime import timedelta
            self.consignment_end_date = self.received_date + timedelta(days=self.consignment_period_days)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        """Check if consignment period has expired."""
        if self.consignment_end_date:
            return timezone.now().date() > self.consignment_end_date
        return False


class ConsignmentItem(AuditedModel):
    """
    Individual book items within a consignment batch.
    """
    batch = models.ForeignKey(
        ConsignmentBatch,
        on_delete=models.CASCADE,
        related_name="items",
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.PROTECT,
        related_name="consignment_items",
    )

    # Quantity
    quantity_consigned = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
    )
    quantity_sold = models.PositiveIntegerField(default=0)
    quantity_returned = models.PositiveIntegerField(default=0)
    quantity_damaged = models.PositiveIntegerField(default=0)

    # Override terms for this specific item
    author_share_override = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0")), MaxValueValidator(Decimal("1"))],
        help_text="Override author share for this item",
    )
    unit_price_override = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Override retail price for this item",
    )

    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["book__title"]
        verbose_name = "Consignment Item"
        verbose_name_plural = "Consignment Items"

    def __str__(self):
        return f"{self.quantity_consigned}x {self.book.title}"

    @property
    def quantity_on_hand(self):
        """Calculate current inventory on hand."""
        return self.quantity_consigned - self.quantity_sold - self.quantity_returned - self.quantity_damaged

    @property
    def effective_unit_price(self):
        """Get effective unit price for this item."""
        if self.unit_price_override is not None:
            return self.unit_price_override
        # Check for BookApproval override
        try:
            approval = BookApproval.objects.get(book=self.book, org=self.batch.org)
            return approval.effective_retail_price
        except BookApproval.DoesNotExist:
            return self.book.retail_price

    def get_effective_author_share(self):
        """
        Get effective author share for this item.
        Priority: Item override > BookApproval override > AuthorOrg override > Org default
        """
        if self.author_share_override is not None:
            return self.author_share_override

        # Check BookApproval
        try:
            approval = BookApproval.objects.get(book=self.book, org=self.batch.org)
            if approval.author_share_override is not None:
                return approval.author_share_override
        except BookApproval.DoesNotExist:
            pass

        # Check AuthorOrganization
        try:
            author_org = AuthorOrganization.objects.get(
                author=self.batch.author,
                org=self.batch.org,
            )
            if author_org.author_share_override is not None:
                return author_org.author_share_override
        except AuthorOrganization.DoesNotExist:
            pass

        return self.batch.org.default_author_share


class ConsignmentReturn(AuditedModel):
    """
    Record of books returned to an author from consignment.
    """
    batch = models.ForeignKey(
        ConsignmentBatch,
        on_delete=models.CASCADE,
        related_name="returns",
    )
    returned_date = models.DateField(default=timezone.now)

    RETURN_REASON_CHOICES = [
        ("end_period", "End of Consignment Period"),
        ("author_request", "Author Request"),
        ("bookseller_request", "Bookseller Request"),
        ("damaged", "Damaged"),
        ("other", "Other"),
    ]
    reason = models.CharField(
        max_length=20,
        choices=RETURN_REASON_CHOICES,
        default="end_period",
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-returned_date"]
        verbose_name = "Consignment Return"
        verbose_name_plural = "Consignment Returns"

    def __str__(self):
        return f"Return from {self.batch} on {self.returned_date}"


class ConsignmentReturnItem(AuditedModel):
    """
    Individual items in a consignment return.
    """
    return_record = models.ForeignKey(
        ConsignmentReturn,
        on_delete=models.CASCADE,
        related_name="items",
    )
    consignment_item = models.ForeignKey(
        ConsignmentItem,
        on_delete=models.PROTECT,
        related_name="return_items",
    )
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
    )

    CONDITION_CHOICES = [
        ("good", "Good Condition"),
        ("damaged", "Damaged"),
        ("lost", "Lost"),
    ]
    condition = models.CharField(
        max_length=20,
        choices=CONDITION_CHOICES,
        default="good",
    )

    class Meta:
        verbose_name = "Consignment Return Item"
        verbose_name_plural = "Consignment Return Items"

    def __str__(self):
        return f"{self.quantity}x {self.consignment_item.book.title}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update the consignment item's returned/damaged quantity
        if self.condition == "damaged":
            self.consignment_item.quantity_damaged += self.quantity
        else:
            self.consignment_item.quantity_returned += self.quantity
        self.consignment_item.save()
