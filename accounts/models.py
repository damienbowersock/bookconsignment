from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class TimestampedModel(models.Model):
    """Abstract base model with audit timestamps."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class AuditedModel(TimestampedModel):
    """Abstract base model with full audit trail."""
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_created",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_updated",
    )

    class Meta:
        abstract = True


class Organization(AuditedModel):
    """
    A bookseller's organization/business.
    Can have multiple locations and staff members.
    """
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)

    # Contact information
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    website = models.URLField(blank=True)

    # Address
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, default="USA")

    # Default consignment settings
    default_author_share = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        default=Decimal("0.65"),
        validators=[MinValueValidator(Decimal("0")), MaxValueValidator(Decimal("1"))],
        help_text="Default author share (e.g., 0.65 for 65%)",
    )
    default_consignment_period_days = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Default consignment period in days. Leave blank for perpetual.",
    )

    # Payment settings
    PAYMENT_CYCLE_CHOICES = [
        ("monthly", "Monthly"),
        ("biweekly", "Bi-weekly"),
        ("weekly", "Weekly"),
        ("quarterly", "Quarterly"),
        ("on_demand", "On Demand"),
    ]
    payment_cycle = models.CharField(
        max_length=20,
        choices=PAYMENT_CYCLE_CHOICES,
        default="monthly",
    )
    minimum_payout_amount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal("10.00"),
        help_text="Minimum balance required to trigger a payout",
    )

    # Status
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Organization.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class Location(AuditedModel):
    """
    A physical location where a bookseller sells books.
    An organization can have multiple locations.
    """
    org = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="locations",
    )
    name = models.CharField(max_length=200)

    # Address
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, default="USA")

    # Contact
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)

    # Integration identifiers (for future Shopify, etc.)
    external_id = models.CharField(
        max_length=255,
        blank=True,
        help_text="External system identifier (e.g., Shopify location ID)",
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["org__name", "name"]
        unique_together = [["org", "name"]]

    def __str__(self):
        return f"{self.name} ({self.org.name})"


class AuthorProfile(AuditedModel):
    """
    Profile for authors who consign books with booksellers.
    An author can work with multiple organizations.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="author_profile",
    )

    # Contact info
    phone = models.CharField(max_length=50, blank=True)
    website = models.URLField(blank=True)

    # Address (for returns/correspondence)
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, default="USA")

    # Payment info
    PAYMENT_METHOD_CHOICES = [
        ("venmo", "Venmo"),
        ("paypal", "PayPal"),
        ("ach", "ACH Bank Transfer"),
        ("check", "Check"),
    ]
    preferred_payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default="venmo",
    )
    payment_handle = models.CharField(
        max_length=255,
        blank=True,
        help_text="Venmo username, PayPal email, etc.",
    )

    # Bio for display
    bio = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["user__last_name", "user__first_name"]

    def __str__(self):
        return self.user.get_full_name() or self.user.username

    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username

    @property
    def email(self):
        return self.user.email


class StaffProfile(AuditedModel):
    """
    Profile for bookseller staff members.
    Staff belong to an organization and can manage inventory, sales, payouts.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="staff_profile",
    )
    org = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="staff",
    )

    # Role/permissions
    ROLE_CHOICES = [
        ("owner", "Owner"),
        ("manager", "Manager"),
        ("staff", "Staff"),
    ]
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="staff",
    )

    # Which locations this staff can access (blank = all locations)
    locations = models.ManyToManyField(
        Location,
        blank=True,
        related_name="staff",
        help_text="Leave blank for access to all locations",
    )

    phone = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["org__name", "user__last_name", "user__first_name"]
        verbose_name_plural = "Staff profiles"

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.org.name})"

    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username

    def can_access_location(self, location):
        """Check if staff can access a specific location."""
        if not self.locations.exists():
            # No specific locations = access to all
            return location.org == self.org
        return location in self.locations.all()


class AuthorOrganization(AuditedModel):
    """
    Many-to-many relationship between authors and organizations.
    Tracks which authors work with which booksellers.
    """
    author = models.ForeignKey(
        AuthorProfile,
        on_delete=models.CASCADE,
        related_name="organization_memberships",
    )
    org = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="author_memberships",
    )

    STATUS_CHOICES = [
        ("pending", "Pending Approval"),
        ("active", "Active"),
        ("suspended", "Suspended"),
        ("terminated", "Terminated"),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )

    # Override organization defaults for this author
    author_share_override = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0")), MaxValueValidator(Decimal("1"))],
        help_text="Override default author share for this author",
    )
    consignment_period_days_override = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Override default consignment period for this author",
    )

    joined_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["org__name", "author__user__last_name"]
        unique_together = [["author", "org"]]
        verbose_name = "Author-Organization Relationship"
        verbose_name_plural = "Author-Organization Relationships"

    def __str__(self):
        return f"{self.author} @ {self.org}"

    @property
    def effective_author_share(self):
        """Get the effective author share (override or org default)."""
        if self.author_share_override is not None:
            return self.author_share_override
        return self.org.default_author_share

    @property
    def effective_consignment_period_days(self):
        """Get the effective consignment period (override or org default)."""
        if self.consignment_period_days_override is not None:
            return self.consignment_period_days_override
        return self.org.default_consignment_period_days
