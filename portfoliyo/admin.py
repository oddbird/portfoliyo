"""
Custom admin site with standard site login and no insecure logout.

"""
from django.conf import settings
from django.shortcuts import redirect
from django.views.decorators.cache import never_cache
from django.contrib import admin, messages
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.views import redirect_to_login

from portfoliyo import xact



class AdminSite(admin.AdminSite):
    """Portfoliyo admin site class."""
    @never_cache
    def login(self, request, extra_context=None):
        """Displays the login form for the given HttpRequest."""
        if request.user.is_authenticated():
            messages.warning(
                request,
                "Your account does not have permissions to access that page. "
                "Please log in with a different account, or visit a different "
                "page. "
                )
        return redirect_to_login(
            request.get_full_path(),
            settings.LOGIN_URL,
            REDIRECT_FIELD_NAME,
            )


    @never_cache
    def logout(self, request, extra_context=None):
        """
        Make admin 'logout' a no-op.

        We replace the link with a "back to Portfoliyo" link.

        The default AdminSite.logout implementation exposes us to logout CSRF.

        """
        return redirect("home")


    def admin_view(self, *args, **kwargs):
        """Wrap all admin views in a transaction."""
        wrapped = super(AdminSite, self).admin_view(*args, **kwargs)
        return xact.xact(wrapped)


site = admin.site = AdminSite()
autodiscover = admin.autodiscover
