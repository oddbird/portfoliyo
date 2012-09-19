"""
Tests for ajax view utilities.

"""
from django.template.response import TemplateResponse
from django.test import RequestFactory

from portfoliyo.view import ajax


class TestAjaxDecorator(object):
    """Tests for ajax template-swapping view decorator."""
    @property
    def view(self):
        """A simple TemplateResponse-returning view, decorated with @ajax."""
        @ajax.ajax("ajax_template.html")
        def view(request):
            return TemplateResponse(request, "normal_template.html")

        return view


    def test_swaps_template(self):
        """Decorator changes TemplateResponse to given template, if ajax."""
        request = RequestFactory().get(
            "/", HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        response = self.view(request)
        assert response.template_name == "ajax_template.html"


    def test_only_ajax(self):
        """Decorator has no effect on non-Ajax response."""
        request = RequestFactory().get("/")
        response = self.view(request)
        assert response.template_name == "normal_template.html"
