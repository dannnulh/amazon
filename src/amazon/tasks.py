from celery import shared_task

from .models import Item
from .utils import get_items, get_item_new_reviews, send_slack_notification


@shared_task
def amazon_items_task():
    get_items()


@shared_task
def amazon_item_review_task(item_id=None):
    if item_id:
        try:
            item = Item.objects.get(asin1=item_id)
            get_item_new_reviews(item)
        except Item.DoesNotExist:
            pass
    else:
        for item in Item.objects.all():
            get_item_new_reviews(item)
    send_slack_notification()
