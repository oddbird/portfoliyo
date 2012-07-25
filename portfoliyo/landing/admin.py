"""Landing page admin."""
from django.contrib import admin

from .models import Lead



class LeadAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": [("email", "following_up"), "notes", "signed_up"]})]
    readonly_fields = ["signed_up"]



admin.site.register(Lead, LeadAdmin)
