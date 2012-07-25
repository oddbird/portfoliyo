"""Landing page admin."""
from django.contrib import admin

from .models import Lead



class LeadAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": [("email", "following_up"), "notes", "signed_up"]})]
    readonly_fields = ["signed_up"]
    list_filter = ["following_up"]
    date_hierarchy = "signed_up"
    list_display = ["email", "following_up", "signed_up", "notes"]
    list_editable = ["following_up"]
    search_fields = ["email"]



admin.site.register(Lead, LeadAdmin)
