from django.contrib import admin

from api.models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ('pk', 'username', 'email',
                    'role', 'is_active', 'is_staff')
    search_fields = ('email',)


admin.site.register(User, UserAdmin)
