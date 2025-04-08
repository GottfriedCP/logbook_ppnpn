from django.forms import ModelForm

from .models import Catatan


class CatatanForm(ModelForm):
    class Meta:
        model = Catatan
        exclude = ["nippnpn", "verified", "verified_at"]
