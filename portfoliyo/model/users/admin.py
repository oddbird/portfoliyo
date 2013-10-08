from django import forms

from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import forms as auth_forms
from django.contrib.auth import models as auth_models

from . import models


class RelationshipsFromInline(admin.TabularInline):
    model = models.Relationship
    fk_name = 'to_profile'
    extra = 0
    raw_id_fields = ['from_profile', 'groups']


class RelationshipsToInline(admin.TabularInline):
    model = models.Relationship
    fk_name = 'from_profile'
    extra = 0
    raw_id_fields = ['to_profile', 'groups']


class ProfileAdmin(admin.ModelAdmin):
    inlines=[RelationshipsFromInline, RelationshipsToInline]
    list_display=[
        '__unicode__',
        'name',
        'email',
        'phone',
        'role',
        'school',
        'school_staff',
        ]
    list_filter=['school', 'school_staff', 'declined']
    search_fields = ['user__email', 'phone']
    raw_id_fields = ['school', 'user', 'invited_by']


    def email(self, profile):
        return profile.user.email
    email.admin_order_field = 'user__email'


    def save_model(self, request, obj, form, change):
        """Save profile; ensure phone is never empty string."""
        obj.phone = obj.phone or None
        return super(ProfileAdmin, self).save_model(request, obj, form, change)


    def delete_model(self, request, obj):
        """Delete profile; also delete related User."""
        obj.user.delete()


    def get_actions(self, request):
        """Disable delete-selected action; dangerous and doesn't delete user."""
        actions = super(ProfileAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions



admin.site.register(models.Profile, ProfileAdmin)
admin.site.register(models.Group)
admin.site.register(models.School)



class UserChangeForm(forms.ModelForm):
    password = auth_forms.ReadOnlyPasswordHashField(
        help_text=
        "Raw passwords are not stored, so there is no way to see "
        "this user's password, but you can change the password "
        "using <a href=\"password/\">this form</a>.",
        )


    def clean_password(self):
        return self.initial["password"]


    def clean_email(self):
        return self.cleaned_data.get('email', None) or None


    class Meta:
        model = auth_models.User


class UserAdmin(auth_admin.UserAdmin):
    list_display = ('email', 'name', 'is_superuser', 'is_staff', 'is_active')
    search_fields = ('email',)
    ordering = ('email',)
    form = UserChangeForm
    fieldsets = [(None, {'fields': (
                    'email',
                    'password',
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'last_login',
                    'date_joined',
                    )})]


    def name(self, obj):
        try:
            return obj.profile.name
        except models.Profile.DoesNotExist:
            return '<no profile>'
    name.admin_order_field = 'profile__name'


if auth_models.User in admin.site._registry: # pragma: no cover
    admin.site.unregister(auth_models.User)

admin.site.register(auth_models.User, UserAdmin)

# we don't use contrib.auth groups; confusing to have them in the admin
if auth_models.Group in admin.site._registry: # pragma: no cover
    admin.site.unregister(auth_models.Group)
