from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect

from .models import Item
from .tasks import amazon_item_review_task, amazon_items_task
from .utils import get_save_order


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
        if settings.DEBUG:
            amazon_item_review_task(item_id)
        else:
            amazon_item_review_task.delay(item_id)
    except Item.DoesNotExist:
        pass

    return redirect('home')


@user_passes_test(lambda u: u.is_staff)
def search_order(request, template='amazon/search_order.html', extra_context=None):
    amazon_order_id = None
    order = None
    if request.method == 'POST':
        amazon_order_id = request.POST.get('amazon_order_id', None)
        amazon_order_id = amazon_order_id.strip()
        if amazon_order_id:
            order = get_save_order(amazon_order_id=amazon_order_id)

    context = {
        'amazon_order_id': amazon_order_id,
        'order': order
    }

    if extra_context:
        context.update(extra_context)

    return render(request, template, context)
