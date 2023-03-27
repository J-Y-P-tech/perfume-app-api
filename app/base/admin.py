"""
Django admin customization.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# Import built it class UserAdmin and name it as BaseUserAdmin
# we will cal our class UserAdmin, and we don't want to conflict

from django.utils.translation import gettext_lazy as _
# gettext_lazy will translate django if needed

from . import models


class UserAdmin(BaseUserAdmin):
    """Define the admin pages for users."""
    ordering = ['id']
    list_display = ['email', 'name']
    fieldsets = (
        # None because will not specify title
        (None, {'fields': ('email', 'password')}),
        (
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                )
            }
        ),
        (_('Important_dates'), {'fields': ('last_login',)}),
    )
    readonly_fields = ['last_login']
    # This field will not be able to be modified
    add_fieldsets = (
        (None, {
            # Assign custom CSS classes in Django admin
            'classes': ('wide',),
            'fields': (
                'email',
                'password1',
                'password2',
                'name',
                'is_active',
                'is_staff',
                'is_superuser',
            ),
        }),
    )


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Perfume)
admin.site.register(models.Designer)
# admin.site.register(models.Note)

