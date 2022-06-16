from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
# Register your models here.
from .models import Account


class AccountAdmin(UserAdmin):
    list_display = ('username', 'role', 'email', 'phone',
                    'created_at', 'last_edit_at')
    search_fields = ('uid', 'username', 'email', 'phone')
    list_filter = ['role', 'is_staff', 'is_superuser']
    fieldsets = UserAdmin.fieldsets


admin.site.register(Account, AccountAdmin)