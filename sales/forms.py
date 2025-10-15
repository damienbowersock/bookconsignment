from django import forms
from .models import InventoryReceipt, Sale

class InventoryReceiptForm(forms.ModelForm):
    class Meta:
        model = InventoryReceipt
        fields = ["book","location","qty","unit_cost"]

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ["book","location","qty","unit_price","source"]
