from django.db import models
from accounts.models import AuthorProfile

class Book(models.Model):
    author = models.ForeignKey(AuthorProfile, on_delete=models.PROTECT, related_name="books")
    title = models.CharField(max_length=255)
    isbn = models.CharField(max_length=20, blank=True)
    retail_price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.title} ({self.author})"
