from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect

from .models import Item
from .tasks import amazon_item_review_task, amazon_items_task


@user_passes_test(lambda u: u.is_staff)
def get_items(request):
    if settings.DEBUG:
        amazon_items_task()
    else:
        amazon_items_task.delay()

    return redirect('home')


@user_passes_test(lambda u: u.is_staff)
def get_reviews(request):
    item_id = request.GET.get('item_id', None)
    try:
        item = Item.objects.get(asin1=item_id)
        if settings.DEBUG:
            amazon_item_review_task(item)
        else:
            amazon_item_review_task.delay(item)
    except Item.DoesNotExist:
        pass

    return redirect('home')
