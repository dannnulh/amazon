from django.contrib import admin

from .models import Item, Review


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'asin1', 'item_name', 'top_critical_review_id', 'created', 'modified')
    search_fields = ['item_name', 'asin1']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'item', 'title', 'author', 'post_date', 'comment_count', 'rating', 'created', 'modified')
    search_fields = ['author', 'title']

