from django.contrib import admin

# Register your models here.
from .models import Account

class AccountAdmin(admin.ModelAdmin):
    list_display=('username', 'email', 'phone', 'created_at', 'last_edit_at')
    search_fields=('username', 'email', 'phone')

admin.site.register(Account, AccountAdmin)