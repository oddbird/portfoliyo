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
    """
    Has ``context_data`` attribute which will be added to template context.

    Also provides initial data, if available, in the template context.

    """
    def __init__(self, *a, **kw):
        super(CheckboxSelectMultiple, self).__init__(*a, **kw)
        self.context_data = {}


    def get_context_data(self):
        data = self.context_data.copy()
        data['initial'] = set(map(str, getattr(self, 'initial', None) or []))
        return data
