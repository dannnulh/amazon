from __future__ import unicode_literals

from django.db import models

from model_utils.models import TimeStampedModel


class Item(TimeStampedModel):
    item_name = models.TextField()
    item_description = models.TextField(null=True, blank=True)
    listing_id = models.CharField(max_length=255)
    seller_sku = models.CharField(max_length=255)
    price = models.FloatField(default=0.0)
    quantity = models.IntegerField(null=True, blank=True)
    open_date = models.CharField(max_length=30)
    image_url = models.URLField(null=True, blank=True)
    item_is_marketplace = models.CharField(max_length=255)
    product_id_type = models.CharField(max_length=255)
    zshop_shipping_fee = models.FloatField(null=True, blank=True)
    item_note = models.TextField(null=True, blank=True)
    item_condition = models.CharField(max_length=255, null=True, blank=True)
    zshop_category1 = models.CharField(max_length=255, null=True, blank=True)
    zshop_browse_path = models.CharField(max_length=255, null=True, blank=True)
    zshop_storefront_feature = models.CharField(max_length=255, null=True, blank=True)
    asin1 = models.CharField(max_length=255, db_index=True)
    asin2 = models.CharField(max_length=255, null=True, blank=True)
    asin3 = models.CharField(max_length=255, null=True, blank=True)
    will_ship_internationally = models.CharField(max_length=255, null=True, blank=True)
    expedited_shipping = models.CharField(max_length=255, null=True, blank=True)
    zshop_boldface = models.CharField(max_length=255, null=True, blank=True)
    product_id = models.CharField(max_length=255)
    bid_for_featured_placement = models.CharField(max_length=255, null=True, blank=True)
    add_delete = models.CharField(max_length=255, null=True, blank=True)
    pending_quantity = models.IntegerField(null=True, blank=True)
    fulfillment_channel = models.CharField(max_length=255)
    merchant_shipping_group = models.CharField(max_length=255)
    top_critical_review_id = models.CharField(max_length=255, null=True, blank=True)
    avg_unit_session_percentage = models.FloatField(null=True, blank=True)

    def __unicode__(self):
        return self.asin1

    @property
    def link(self):
        return u'https://www.amazon.co.uk/dp/%s' % self.asin1


class Review(TimeStampedModel):
    id = models.CharField(max_length=255, primary_key=True)
    item = models.ForeignKey(Item)
    author = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    content = models.TextField(null=True, blank=True)
    comment_count = models.IntegerField(default=0)
    post_date = models.DateField()
    rating = models.FloatField(default=5.0)
    send_notification = models.BooleanField(default=False)

    def __unicode__(self):
        return u'%s - %s' % (self.author, self.title)

    @property
    def link(self):
        return u'https://www.amazon.co.uk/gp/customer-reviews/%s/' % self.id


class DetailPageSalesTraffic(TimeStampedModel):
    dt = models.DateField(db_index=True)
    parent_asin = models.CharField(max_length=255)
    child_asin = models.CharField(max_length=255, db_index=True)
    title = models.TextField()
    sku=models.CharField(max_length=255)
    sessions=models.PositiveIntegerField()
    session_percentage = models.FloatField()
    page_views = models.PositiveIntegerField()
    page_views_percentage = models.FloatField()
    buy_box_percentage = models.FloatField()
    units_ordered = models.PositiveIntegerField()
    unit_session_percentage = models.FloatField()
    ordered_product_sales = models.FloatField()
    currency = models.CharField(max_length=10)
    total_order_items = models.PositiveIntegerField()

    def __unicode__(self):
        return u'[%s]%s: %s' % (self.dt, self.child_asin, self.total_order_items)


class Cookie(TimeStampedModel):
    content = models.TextField()
