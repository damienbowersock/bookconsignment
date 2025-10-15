from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from accounts.models import Organization

class AuthorSignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True, max_length=150)
    last_name = forms.CharField(required=True, max_length=150)
    phone = forms.CharField(required=False, max_length=50)
    org = forms.ModelChoiceField(
        queryset=Organization.objects.all(),
        required=True,
        help_text="Select the bookstore you consign with."
    )

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "phone", "org", "password1", "password2"]
