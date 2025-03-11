from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.authentication.models import User


# Register your models here.

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'telegram_id', 'is_staff')
    search_fields = ('username', 'email', 'telegram_id')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('email', 'telegram_id')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'is_active')}),
    )