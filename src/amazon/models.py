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
    asin1 = models.CharField(max_length=255)
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

    def __unicode__(self):
        return self.asin1
