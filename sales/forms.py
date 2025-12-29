from django import forms
from .models import Sale
from catalog.models import Book
from accounts.models import Location


class ConsignmentReceiptForm(forms.Form):
    """Form for receiving consignment inventory."""
    book = forms.ModelChoiceField(
        queryset=Book.objects.all(),
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    location = forms.ModelChoiceField(
        queryset=Location.objects.filter(is_active=True),
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    qty = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={"class": "form-control", "value": 1}),
    )


class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ["book", "location", "quantity", "unit_price", "source"]
        widgets = {
            "book": forms.Select(attrs={"class": "form-control"}),
            "location": forms.Select(attrs={"class": "form-control"}),
            "quantity": forms.NumberInput(attrs={"class": "form-control", "value": 1}),
            "unit_price": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "source": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["location"].queryset = Location.objects.filter(is_active=True)
