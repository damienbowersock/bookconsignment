from django.db import models
from accounts.models import AuthorProfile

class Payout(models.Model):
    METHOD_CHOICES = [("venmo","Venmo"),("ach","ACH"),("check","Check")]
    author = models.ForeignKey(AuthorProfile, on_delete=models.PROTECT, related_name="payouts")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, default="venmo")
    reference = models.CharField(max_length=120, blank=True)   # store Venmo note/txn id
    paid_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author} - {self.amount} ({self.method})"
