from django.contrib import admin

from .models import Item, Review, DetailPageSalesTraffic


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'asin1', 'item_name', 'top_critical_review_id', 'created', 'modified')
    search_fields = ['item_name', 'asin1']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'item', 'title', 'author', 'post_date', 'comment_count', 'rating', 'created', 'modified')
    search_fields = ['author', 'title']


@admin.register(DetailPageSalesTraffic)
class DetailPageSalesTrafficAdmin(admin.ModelAdmin):
    search_fields = ('child_asin', 'title', 'sku')
    list_display = ('dt', 'child_asin', 'title', 'sku', 'sessions', 'session_percentage', 'page_views',
                    'page_views_percentage', 'buy_box_percentage', 'units_ordered', 'unit_session_percentage',
                    'ordered_product_sales', 'currency', 'total_order_items', 'created', 'modified')
