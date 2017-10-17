from django.contrib import admin

from .models import Item, Review, DetailPageSalesTraffic, Order


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = (
    'id', 'asin1', 'item_name', 'top_critical_review_id', 'avg_unit_session_percentage', 'created', 'modified')
    search_fields = ['item_name', 'asin1']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'item', 'title', 'author', 'post_date', 'comment_count', 'rating', 'created', 'modified')
    search_fields = ['author', 'title']


@admin.register(DetailPageSalesTraffic)
class DetailPageSalesTrafficAdmin(admin.ModelAdmin):
    search_fields = ('child_asin', 'title')
    list_display = ('dt', 'child_asin', 'title', 'sessions', 'session_percentage', 'page_views',
                    'page_views_percentage', 'buy_box_percentage', 'units_ordered', 'unit_session_percentage',
                    'ordered_product_sales', 'currency', 'total_order_items', 'created', 'modified')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
    'id', 'AmazonOrderId', 'PurchaseDate', 'OrderStatus', 'MarketplaceId', 'BuyerEmail', 'BuyerName', 'OrderType')
