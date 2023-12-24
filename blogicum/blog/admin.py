from django.contrib import admin

from blog.models import (
    Category,
    Post,
    Location,
)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'pub_date',
        'author',
        'category',
        'is_published',
        'created_at',
    )
    search_fields = (
        'title',
        'author',
        'category',
    )
    list_filter = (
        'author',
        'category',
        'is_published',
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'is_published',
        'created_at',
    )
    search_fields = ('title',)
    prepopulated_fields = {'slug': ['title', ], }
    list_filter = ('is_published',)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'is_published',
        'created_at',
    )
