from django.contrib import admin

from .models import Item


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'asin1', 'item_name', 'created', 'modified')
    search_fields = ['item_name', 'asin1']
