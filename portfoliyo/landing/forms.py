"""Landing page forms."""
import floppyforms as forms

from .models import Lead


class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = ["email"]
        widgets = {"email": forms.EmailInput}


    def __init__(self, *args, **kwargs):
        """Override some error messages."""
        super(LeadForm, self).__init__(*args, **kwargs)

        error_msg = "That doesn't look like an email address; double-check it?"
        self.fields["email"].error_messages["required"] = error_msg
        self.fields["email"].error_messages["invalid"] = error_msg
