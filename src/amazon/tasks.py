from celery import shared_task

from .models import Item
from .utils import get_items, get_item_new_reviews


@shared_task
def amazon_items_task():
    get_items()


@shared_task
def amazon_item_review_task(item=None):
    if item:
        get_item_new_reviews(item)
    else:
        for item in Item.objects.all():
            get_item_new_reviews(item)
