from django.conf import settings
from django.db import models

class Organization(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Location(models.Model):
    org = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="locations")
    name = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.name} ({self.org.name})"

class AuthorProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    org = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="authors")
    phone = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"
