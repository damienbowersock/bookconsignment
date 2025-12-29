from django import forms
from .models import Book


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            "title", "subtitle", "description",
            "isbn", "retail_price",
            "format", "page_count",
            "cover_image",
            "publisher", "publication_date",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "subtitle": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "isbn": forms.TextInput(attrs={"class": "form-control"}),
            "retail_price": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "format": forms.Select(attrs={"class": "form-control"}),
            "page_count": forms.NumberInput(attrs={"class": "form-control"}),
            "cover_image": forms.FileInput(attrs={"class": "form-control"}),
            "publisher": forms.TextInput(attrs={"class": "form-control"}),
            "publication_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }
