from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group

from .models import Category, Comment, Genre, Title, Review, User


class UserAdmin(BaseUserAdmin):
    list_display = ('pk', 'username', 'email', 'first_name',
                    'last_name', 'bio', 'role', 'is_staff', 'is_superuser')
    list_filter = ('is_staff',)
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Права и роли', {'fields': ('role', 'is_staff', 'is_superuser')}),
        ('О пользователе', {'fields': ('bio',)}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',),
                'fields': ('email', )}),
    ) + BaseUserAdmin.add_fieldsets
    search_fields = ('email',)
    ordering = ('email',)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


class GenreAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


class TitleAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'category', 'description', 'year')
    search_fields = ('name',)


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'text', 'author', 'score', 'pub_date')
    search_fields = ('text',)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'review', 'text', 'author', 'pub_date')
    search_fields = ('text',)


admin.site.register(User, UserAdmin)
admin.site.unregister(Group)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Title, TitleAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Comment, CommentAdmin)
