from django.contrib import admin

from api.models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ('pk', 'username', 'email', 'bio', 'role')
    search_fields = ('username',)


admin.site.register(User, UserAdmin)
