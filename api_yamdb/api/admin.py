from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

User = get_user_model()


class UserAdmin(BaseUserAdmin):
    list_display = ('pk', 'username', 'email',
                    'role', 'is_active', 'is_staff')
    search_fields = ('email',)


admin.site.register(User, UserAdmin)
