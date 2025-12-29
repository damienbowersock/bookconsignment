import uuid
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

from accounts.models import AuditedModel, AuthorProfile, Organization


def book_cover_upload_path(instance, filename):
    """Generate upload path for book cover images."""
    ext = filename.split(".")[-1] if "." in filename else "jpg"
    return f"covers/{instance.author.id}/{uuid.uuid4()}.{ext}"


class Book(AuditedModel):
    """
    A book title in the catalog.
    Created by authors, can be consigned to multiple organizations.
    """
    author = models.ForeignKey(
        AuthorProfile,
        on_delete=models.PROTECT,
        related_name="books",
    )

    # Basic info
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)

    # Identifiers
    isbn = models.CharField(
        max_length=20,
        blank=True,
        db_index=True,
        help_text="ISBN-10 or ISBN-13",
    )
    isbn13 = models.CharField(
        max_length=13,
        blank=True,
        db_index=True,
        help_text="ISBN-13 (normalized)",
    )
    sku = models.CharField(
        max_length=50,
        blank=True,
        help_text="Internal SKU if different from ISBN",
    )

    # Pricing
    retail_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    wholesale_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.01"))],
        help_text="Author's cost (optional, for reporting)",
    )

    # Physical attributes
    FORMAT_CHOICES = [
        ("paperback", "Paperback"),
        ("hardcover", "Hardcover"),
        ("ebook", "E-book"),
        ("audiobook", "Audiobook"),
        ("other", "Other"),
    ]
    format = models.CharField(
        max_length=20,
        choices=FORMAT_CHOICES,
        default="paperback",
    )
    page_count = models.PositiveIntegerField(null=True, blank=True)
    dimensions = models.CharField(
        max_length=50,
        blank=True,
        help_text="e.g., 6x9 inches",
    )
    weight_oz = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Weight in ounces",
    )

    # Cover image
    cover_image = models.ImageField(
        upload_to=book_cover_upload_path,
        blank=True,
        null=True,
    )
    cover_image_url = models.URLField(
        blank=True,
        help_text="External URL for cover image (if not uploaded)",
    )

    # Publication info
    publisher = models.CharField(max_length=255, blank=True)
    publication_date = models.DateField(null=True, blank=True)
    edition = models.CharField(max_length=50, blank=True)
    language = models.CharField(max_length=50, default="English")

    # Categories
    categories = models.ManyToManyField(
        "Category",
        blank=True,
        related_name="books",
    )

    # Status
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the book is currently available for consignment",
    )

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return f"{self.title} ({self.author})"

    @property
    def display_isbn(self):
        """Return the best ISBN to display."""
        return self.isbn13 or self.isbn or self.sku or "N/A"

    @property
    def cover_url(self):
        """Return cover image URL (uploaded or external)."""
        if self.cover_image:
            return self.cover_image.url
        return self.cover_image_url or None


class Category(models.Model):
    """
    Book category/genre for organization.
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
    )
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Categories"

    def __str__(self):
        if self.parent:
            return f"{self.parent} > {self.name}"
        return self.name


class BookApproval(AuditedModel):
    """
    Tracks approval status of a book for a specific organization.
    Booksellers must approve books before they can be consigned.
    """
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="approvals",
    )
    org = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="book_approvals",
    )

    STATUS_CHOICES = [
        ("pending", "Pending Review"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("suspended", "Suspended"),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )

    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="book_reviews",
    )
    rejection_reason = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    # Override pricing for this organization
    org_retail_price_override = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Override retail price for this organization",
    )

    # Override consignment terms for this specific book
    author_share_override = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Override author share for this book at this org",
    )

    class Meta:
        ordering = ["-created_at"]
        unique_together = [["book", "org"]]
        verbose_name = "Book Approval"
        verbose_name_plural = "Book Approvals"

    def __str__(self):
        return f"{self.book.title} @ {self.org.name} ({self.status})"

    @property
    def effective_retail_price(self):
        """Get effective retail price (override or book default)."""
        if self.org_retail_price_override is not None:
            return self.org_retail_price_override
        return self.book.retail_price

    def get_effective_author_share(self, author_org_membership=None):
        """
        Get effective author share for this book at this org.
        Priority: BookApproval override > AuthorOrganization override > Org default
        """
        if self.author_share_override is not None:
            return self.author_share_override
        if author_org_membership and author_org_membership.author_share_override is not None:
            return author_org_membership.author_share_override
        return self.org.default_author_share
