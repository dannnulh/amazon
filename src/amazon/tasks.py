import datetime
from celery import shared_task

from .models import Item
from .utils import get_items, get_item_new_reviews, download_business_report, check_avg_usp


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


@shared_task
def download_business_report_task():
    dt = datetime.date.today() - datetime.timedelta(days=1)
    download_business_report(dt)
    check_avg_usp(dt)
