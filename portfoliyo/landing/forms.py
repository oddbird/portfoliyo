"""Landing page forms."""
import floppyforms as forms

from .models import Lead


class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = ["email"]
        widgets = {"email": forms.EmailInput}
