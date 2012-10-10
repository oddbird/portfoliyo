import floppyforms as forms



class TemplateLabelMixin(object):
    def label_from_instance(self, obj):
        """Return the object itself, not a string; template renders to label."""
        return obj



class TemplateLabelModelChoiceField(TemplateLabelMixin, forms.ModelChoiceField):
    """A ModelChoiceField that relies on rendering template to handle label."""



class TemplateLabelModelMultipleChoiceField(TemplateLabelMixin,
                                            forms.ModelMultipleChoiceField):
    """A ModelMultipleChoiceField that allows template to render label."""
