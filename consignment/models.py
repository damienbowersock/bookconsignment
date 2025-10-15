from django.db import models
from accounts.models import AuthorProfile
from catalog.models import Book

class ConsignmentAgreement(models.Model):
    author = models.ForeignKey(AuthorProfile, on_delete=models.CASCADE, related_name="agreements")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="agreements")
    author_share = models.DecimalField(max_digits=5, decimal_places=2)  # e.g. 0.60 for 60%
    start = models.DateField()
    end = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.author} - {self.book} ({self.author_share*100:.0f}%)"
