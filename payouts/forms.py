from django import forms
from .models import Payout

class PayoutForm(forms.ModelForm):
    class Meta:
        model = Payout
        fields = ["author","amount","method","reference"]
