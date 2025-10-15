from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from accounts.models import Organization, Location

class Command(BaseCommand):
    help = "Create default groups (Authors, Staff) and a demo org/location."

    def handle(self, *args, **options):
        authors, _ = Group.objects.get_or_create(name="Authors")
        staff, _ = Group.objects.get_or_create(name="Staff")
        self.stdout.write(self.style.SUCCESS(f"Groups ensured: {authors.name}, {staff.name}"))

        org, _ = Organization.objects.get_or_create(name="Demo Org")
        loc, _ = Location.objects.get_or_create(org=org, name="Main Store")
        self.stdout.write(self.style.SUCCESS(f"Org/Location ensured: {org} / {loc}"))
