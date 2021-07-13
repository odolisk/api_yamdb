from django.contrib import admin

from .models import Profile


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'bio', 'role')
    search_fields = ('user',)


admin.site.register(Profile, ProfileAdmin)
