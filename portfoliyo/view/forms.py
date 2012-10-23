import floppyforms as forms



class TemplateRenderedMixin(object):
    """Some conveniences for template-rendered fields."""
    def _get_initial(self):
        return self._initial


    def _set_initial(self, value):
        self.widget.initial = value
        self._initial = value


    initial = property(_get_initial, _set_initial)


    def label_from_instance(self, obj):
        """Return the object itself, not a string; template renders to label."""
        return obj



class ModelChoiceField(TemplateRenderedMixin, forms.ModelChoiceField):
    """A ModelChoiceField that relies on rendering template to handle label."""



class ModelMultipleChoiceField(TemplateRenderedMixin,
                               forms.ModelMultipleChoiceField):
    """A ModelMultipleChoiceField that allows template to render label."""



class CheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    """Provides initial data, if available, in the template context."""
    def get_context_data(self):
        return {'initial': set(map(str, getattr(self, 'initial', None) or []))}
