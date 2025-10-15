from django.db import models
from accounts.models import Location
from catalog.models import Book

class InventoryReceipt(models.Model):
    book = models.ForeignKey(Book, on_delete=models.PROTECT, related_name="receipts")
    location = models.ForeignKey(Location, on_delete=models.PROTECT, related_name="receipts")
    qty = models.PositiveIntegerField()
    unit_cost = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    received_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.qty} x {self.book} @ {self.location}"

class Sale(models.Model):
    book = models.ForeignKey(Book, on_delete=models.PROTECT, related_name="sales")
    location = models.ForeignKey(Location, on_delete=models.PROTECT, related_name="sales")
    qty = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    sold_at = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=50, blank=True)  # e.g. POS name / channel

    def __str__(self):
        return f"Sale {self.qty} x {self.book} @ {self.location}"
