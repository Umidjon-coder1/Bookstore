from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('book', 'user', 'rating', 'is_approved', 'created_at')
    list_filter = ('rating', 'is_approved')
    search_fields = ('book__title', 'user__email', 'body')
    list_editable = ('is_approved',)
    readonly_fields = ('created_at', 'updated_at')
