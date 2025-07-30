from django import forms
from .models import Pembayaran

class PembayaranForm(forms.ModelForm):
    class Meta:
        model = Pembayaran
        fields = ['metode', 'bukti_transfer']
