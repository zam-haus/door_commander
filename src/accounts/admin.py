from django.contrib import admin

# Register your models here.

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

from django.utils.translation import gettext_lazy as _


class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None,
         {'fields':
              ('username', 'password', 'last_login', 'password_last_changed', 'date_joined')}),
        (_('Personal info'),
         {'fields':
              ('display_name', 'full_name', 'email')
          }),
        (_('Permissions'),
         {'fields':
              ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
          }),
    )
    list_display = ('username', 'email', 'display_name', 'full_name', 'is_staff')
    list_filter = (
        'is_staff', 'is_superuser', 'is_active', 'groups', 'password_last_changed', 'last_login', 'date_joined')
    search_fields = ('username', 'display_name', 'full_name', 'email')
    readonly_fields = BaseUserAdmin.readonly_fields + ('password_last_changed', "last_login", "date_joined")



admin.site.register(User, UserAdmin)
