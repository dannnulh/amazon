import StringIO
import csv
import datetime
import requests
from requests import session
from bs4 import BeautifulSoup
from django.conf import settings
from django.db.models import Sum
from lxml import html
from time import sleep
from mws import mws
from dateutil import parser as dateparser

from .models import Item, Review, DetailPageSalesTraffic, Cookie


def _get_float(value, default=None):
    value = value.replace(',', '')
    result = default
    try:
        result = float(value)
    except:
        pass
    return result


def _get_int(value, default=None):
    value = value.replace(',', '')
    result = default
    try:
        result = int(value)
    except:
        pass
    return result


def _get_percent(value, default=None):
    value = value.replace('%', '')
    return _get_float(value, default)


def _decode(value):
    return value.decode('utf-8', errors='ignore')


def _save_items(reader):
    asin_list = []
    for row in reader:
        row = map(_decode, row)
        asin1 = row[16]
        asin_list.append(asin1)
        try:
            item = Item.objects.get(asin1=asin1)
            item.item_name = row[0]
            item.item_description = row[1]
            item.listing_id = row[2]
            item.seller_sku = row[3]
            item.price = _get_float(row[4], 0.0)
            item.quantity = _get_int(row[5])
            item.open_date = row[6]
            item.image_url = row[7]
            item.item_is_marketplace = row[8]
            item.product_id_type = row[9]
            item.zshop_shipping_fee = _get_float(row[10])
            item.item_note = row[11]
            item.item_condition = row[12]
            item.zshop_category1 = row[13]
            item.zshop_browse_path = row[14]
            item.zshop_storefront_feature = row[15]
            item.asin1 = row[16]
            item.asin2 = row[17]
            item.asin3 = row[18]
            item.will_ship_internationally = row[19]
            item.expedited_shipping = row[20]
            item.zshop_boldface = row[21]
            item.product_id = row[22]
            item.bid_for_featured_placement = row[23]
            item.add_delete = row[24]
            item.pending_quantity = _get_int(row[25])
            item.fulfillment_channel = row[26]
            item.merchant_shipping_group = row[27]
        except Item.DoesNotExist:
            item = Item(
                item_name=row[0],
                item_description=row[1],
                listing_id=row[2],
                seller_sku=row[3],
                price=_get_float(row[4], 0.0),
                quantity=_get_int(row[5]),
                open_date=row[6],
                image_url=row[7],
                item_is_marketplace=row[8],
                product_id_type=row[9],
                zshop_shipping_fee=_get_float(row[10]),
                item_note=row[11],
                item_condition=row[12],
                zshop_category1=row[13],
                zshop_browse_path=row[14],
                zshop_storefront_feature=row[15],
                asin1=row[16],
                asin2=row[17],
                asin3=row[18],
                will_ship_internationally=row[19],
                expedited_shipping=row[20],
                zshop_boldface=row[21],
                product_id=row[22],
                bid_for_featured_placement=row[23],
                add_delete=row[24],
                pending_quantity=_get_int(row[25]),
                fulfillment_channel=row[26],
                merchant_shipping_group=row[27]
            )
        item.save()
    Item.objects.exclude(asin1__in=asin_list).delete()


def _save_review(item, raw):
    try:
        review = Review.objects.get(item=item, id=raw['id'])
        review.author = raw['author']
        review.title = raw['title']
        review.content = raw['content']
        review.comment_count = _get_int(raw['comment_count'], 0)
        review.post_date = dateparser.parse(raw['post_date']).date()
        review.rating = _get_float(raw['rating'], 5.0)
    except Review.DoesNotExist:
        review = Review(
            item=item,
            id=raw['id'],
            author=raw['author'],
            title=raw['title'],
            content=raw['content'],
            comment_count=_get_int(raw['comment_count'], 0),
            post_date=dateparser.parse(raw['post_date']).date(),
            rating=_get_float(raw['rating'], 5.0),
        )
    review.save()
    return review


def _parse_total_review_count(asin):
    total_review_count = 0
    amazon_url = 'https://www.amazon.co.uk/product-reviews/%s/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&showViewpoints=1&sortBy=helpful&pageNumber=1&filterByStar=all_stars' % asin
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
    page = requests.get(amazon_url, headers=headers)
    parser = html.fromstring(page.text)

    TOTAL_REVIEWS = '//span[@data-hook="total-review-count"]/text()'
    total_reviews = parser.xpath(TOTAL_REVIEWS)
    if total_reviews:
        total_review_count = int(total_reviews[0])
    return total_review_count


def _parse_review_data_page(asin):
    total_pages = 1
    amazon_url = 'https://www.amazon.co.uk/product-reviews/%s/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&showViewpoints=1&sortBy=recent&pageNumber=1&filterByStar=all_stars' % asin
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
    page = requests.get(amazon_url, headers=headers)
    parser = html.fromstring(page.text)

    PAGINATION_BAR = '//div[@id="cm_cr-pagination_bar"]'
    pagination_bar = parser.xpath(PAGINATION_BAR)
    if pagination_bar:
        PAGINATION_NUMBERS = './/li[@data-reftag="cm_cr_arp_d_paging_btm"]/a/text()'
        pagination_numbers = pagination_bar[0].xpath(PAGINATION_NUMBERS)
        if pagination_numbers:
            total_pages = int(pagination_numbers[-1])
    return total_pages


def _parse_review_data(asin, page_number=1):
    amazon_url = 'https://www.amazon.co.uk/product-reviews/%s/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&showViewpoints=1&sortBy=recent&pageNumber=%s&filterByStar=all_stars' % (
        asin, page_number)
    print amazon_url
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
    page = requests.get(amazon_url, headers=headers)
    parser = html.fromstring(page.text)

    REVIEW_LIST = '//div[@data-hook="review"]'
    reviews_list = []
    reviews = parser.xpath(REVIEW_LIST)
    for review in reviews:
        XPATH_ID = '@id'
        XPATH_RATING = './/i[@data-hook="review-star-rating"]//text()'
        XPATH_REVIEW_HEADER = './/a[@data-hook="review-title"]//text()'
        XPATH_REVIEW_POSTED_DATE = './/a[contains(@href,"/profile/")]/parent::span/following-sibling::span/text()'
        XPATH_REVIEW_TEXT = './/span[@data-hook="review-body"]//text()'
        XPATH_REVIEW_COMMENTS = './/span[@class="review-comment-total"]//text()'
        XPATH_AUTHOR = './/a[contains(@href,"/profile/")]/parent::span//text()'
        raw_review_id = review.xpath(XPATH_ID)
        raw_review_author = review.xpath(XPATH_AUTHOR)
        raw_review_rating = review.xpath(XPATH_RATING)
        raw_review_header = review.xpath(XPATH_REVIEW_HEADER)
        raw_review_posted_date = review.xpath(XPATH_REVIEW_POSTED_DATE)
        raw_review_text = review.xpath(XPATH_REVIEW_TEXT)
        raw_review_comments = review.xpath(XPATH_REVIEW_COMMENTS)

        # cleaning data
        id = ''.join(raw_review_id)
        rating = ''.join(raw_review_rating).replace('out of 5 stars', '')
        title = ' '.join(' '.join(raw_review_header).split())
        content = ' '.join(' '.join(raw_review_text).split())
        post_date = dateparser.parse(''.join(raw_review_posted_date)).strftime('%d %b %Y')
        author = ' '.join(' '.join(raw_review_author).split()).strip('By').strip()
        comment_count = ''.join(raw_review_comments)

        review_dict = {
            'id': id,
            'comment_count': comment_count,
            'content': content,
            'post_date': post_date,
            'title': title,
            'rating': rating,
            'author': author

        }
        reviews_list.append(review_dict)
    return reviews_list


def parse_top_critical_review(asin):
    amazon_url = 'https://www.amazon.co.uk/product-reviews/%s/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&showViewpoints=1&sortBy=helpful&pageNumber=1&filterByStar=critical' % asin
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
    page = requests.get(amazon_url, headers=headers)
    parser = html.fromstring(page.text)

    REVIEW_LIST = '//div[@data-hook="review"]'
    reviews = parser.xpath(REVIEW_LIST)
    review_dict = None
    if reviews:
        review = reviews[0]
        XPATH_ID = '@id'
        XPATH_RATING = './/i[@data-hook="review-star-rating"]//text()'
        XPATH_REVIEW_HEADER = './/a[@data-hook="review-title"]//text()'
        XPATH_REVIEW_POSTED_DATE = './/a[contains(@href,"/profile/")]/parent::span/following-sibling::span/text()'
        XPATH_REVIEW_TEXT = './/span[@data-hook="review-body"]//text()'
        XPATH_REVIEW_COMMENTS = './/span[@class="review-comment-total"]//text()'
        XPATH_AUTHOR = './/a[contains(@href,"/profile/")]/parent::span//text()'
        raw_review_id = review.xpath(XPATH_ID)
        raw_review_author = review.xpath(XPATH_AUTHOR)
        raw_review_rating = review.xpath(XPATH_RATING)
        raw_review_header = review.xpath(XPATH_REVIEW_HEADER)
        raw_review_posted_date = review.xpath(XPATH_REVIEW_POSTED_DATE)
        raw_review_text = review.xpath(XPATH_REVIEW_TEXT)
        raw_review_comments = review.xpath(XPATH_REVIEW_COMMENTS)

        # cleaning data
        id = ''.join(raw_review_id)
        rating = ''.join(raw_review_rating).replace('out of 5 stars', '')
        title = ' '.join(' '.join(raw_review_header).split())
        content = ' '.join(' '.join(raw_review_text).split())
        post_date = dateparser.parse(''.join(raw_review_posted_date)).strftime('%d %b %Y')
        author = ' '.join(' '.join(raw_review_author).split()).strip('By').strip()
        comment_count = ''.join(raw_review_comments)

        review_dict = {
            'id': id,
            'comment_count': comment_count,
            'content': content,
            'post_date': post_date,
            'title': title,
            'rating': rating,
            'author': author

        }

    return review_dict


def get_items():
    x = mws.Reports(access_key=settings.MWS_ACCESS_KEY, secret_key=settings.MWS_SECRET_KEY,
                    account_id=settings.MWS_ACCOUNT_ID, region='UK')

    resp = x.request_report(report_type='_GET_MERCHANT_LISTINGS_ALL_DATA_')
    request_id = resp.parsed.ReportRequestInfo.ReportRequestId
    sleep(50)

    resp = x.get_report_request_list(requestids=(request_id,))
    report_id = resp.parsed.ReportRequestInfo.GeneratedReportId

    resp = x.get_report(report_id=report_id)
    csv_string = resp.parsed

    f = StringIO.StringIO(csv_string)
    reader = csv.reader(f, delimiter='\t')
    reader.next()
    _save_items(reader)


def get_item_new_reviews(item):
    sleep(5)
    asin = item.asin1
    item_reviews = item.review_set.all().order_by('-post_date')
    if not item_reviews:
        get_item_all_reviews(item)
    else:
        amazon_total_reviews = _parse_total_review_count(asin)
        if item_reviews.count() < amazon_total_reviews:
            total_pages = _parse_review_data_page(asin)
            for page_number in range(1, total_pages + 1):
                amazon_reviews = _parse_review_data(asin, page_number)
                amazon_reviews_id = [r['id'] for r in amazon_reviews]
                reviews_id_db = Review.objects.filter(item=item, id__in=amazon_reviews_id)
                if reviews_id_db.count() == len(amazon_reviews):
                    break
                for raw in amazon_reviews:
                    _save_review(item, raw)

    # check if the item top critical review has been changed
    # if changed and the reivew didn't send before then send slack notification
    sleep(5)
    critical_review_raw = parse_top_critical_review(item.asin1)
    print item, critical_review_raw
    if critical_review_raw:
        critical_review = _save_review(item, critical_review_raw)
        if item.top_critical_review_id == None or item.top_critical_review_id != critical_review.id:
            item.top_critical_review_id = critical_review.id
            item.save()

            if critical_review.send_notification == False:
                text = _generate_slack_text(critical_review)
                _send_slack_dm('dev-dan-alerts', text)
                critical_review.send_notification = True
                critical_review.save()


def get_item_all_reviews(item):
    asin = item.asin1
    total_pages = _parse_review_data_page(asin)
    reviews = []
    for page_number in range(1, total_pages + 1):
        reviews.extend(_parse_review_data(asin, page_number))

    for raw in reviews:
        _save_review(item, raw)

    return reviews


def send_slack_notification():
    for review in Review.objects.filter(rating__lt=4.0, send_notification=False):
        text = _generate_slack_text(review)
        _send_slack_dm('dev-dan-alerts', text)
        review.send_notification = True
        review.save()


def _generate_slack_text(review):
    text = 'The item top critical review changed\n```Item:%s\nItem Link:%s\nAuthor:%s\nTitle:%s\nPosted Date:%s\nRating:%s\nLink:%s```' % (
        review.item.item_name, review.item.link, review.author, review.title, review.post_date, review.rating,
        review.link
    )
    return text


def _send_slack_dm(slack_user_id, text):
    url = 'https://slack.com/api/chat.postMessage'
    params = {
        'token': settings.SLACK_TOKEN,
        'channel': slack_user_id,
        'text': text
    }
    resp = requests.post(url, params)
    return resp


def _save_sales_traffic_data(dt, reader):
    DetailPageSalesTraffic.objects.filter(dt=dt).delete()
    for row in reader:
        if len(row) < 12:
            continue
        sales = row[10].replace('\xc2\xa3', '')
        dpst = DetailPageSalesTraffic(
            dt=dt,
            parent_asin=row[0],
            child_asin=row[1],
            title=row[2],
            sessions=_get_int(row[3]),
            session_percentage=_get_percent(row[4]),
            page_views=_get_int(row[5]),
            page_views_percentage=_get_percent(row[6]),
            buy_box_percentage=_get_percent(row[7]),
            units_ordered=_get_int(row[8]),
            unit_session_percentage=_get_percent(row[9]),
            ordered_product_sales=_get_float(sales),
            currency='\xc2\xa3',
            total_order_items=_get_int(row[11])
        )
        dpst.save()


def _get_cookie():
    cookie = Cookie.objects.all()[0]
    return cookie.content


def download_business_report(dt):
    '''
    Download the busincess report
    :param dt: The date, need to transfer to the string, the format is 'dd/mm/yyyy'
    :return:
    '''
    dt_string = dt.strftime('%d/%m/%Y')
    ds = datetime.date.today().strftime('%d-%m-%Y')

    amazon_seller_central_home_url = 'https://sellercentral.amazon.co.uk/'

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en,zh-CN;q=0.8,zh;q=0.6,ar;q=0.4',
        'Connection': 'keep-alive',
        'Host': 'sellercentral.amazon.co.uk',
        'Referer': 'https://sellercentral.amazon.co.uk/gp/site-metrics/report.html',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }

    login_data = {
        'email': settings.AMAZON_LOGIN_EMAIL,
        'password': settings.AMAZON_LOGIN_PASSWORD
    }

    with session() as s:
        # request the amazon seller central home page at first
        resp = s.get(amazon_seller_central_home_url, headers=headers)

        # use BeautifulSoup to analysis the html and prepare the form data
        soup = BeautifulSoup(resp.content, 'html.parser')
        action = soup.select('form[name=signIn]')[0].get('action')
        form_data = soup.select('form[name=signIn] input')
        for input in form_data:
            if input.attrs.get('name', None) and input.attrs.get('name', None) not in login_data:
                login_data.update({input.attrs['name']: input.attrs['value']})

        # login
        r = s.post(action, data=login_data, headers=headers)
        if r.url == 'https://sellercentral.amazon.co.uk/merchant-picker/status':
            s.get(url='https://sellercentral.amazon.co.uk/merchant-picker/status/skip-2sv', headers=headers)

        report_url = 'https://sellercentral.amazon.co.uk/gp/site-metrics/load/csv/BusinessReport-%s.csv' % ds
        headers.update({
            'Cache-Control': 'max-age=0',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://sellercentral.amazon.co.uk'
        })

        data = {
            'reportID': '102:DetailSalesTrafficByChildItem',
            'sortIsAscending': '0',
            'sortColumn': '12',
            'fromDate': dt_string,
            'toDate': dt_string,
            'cols': '/c0/c1/c2/c3/c4/c5/c6/c7/c8/c9/c10/c11',
            'rows': '',
            'dateUnit': '1',
            'currentPage': '0',
            'runDate': ''
        }

        resp = s.post(url=report_url, data=data, headers=headers)

        if resp.status_code == 200:
            f = StringIO.StringIO(resp.content)
            reader = csv.reader(f)
            header = reader.next()
            if header[1] != '(Child) ASIN':
                raise Exception('Session timeout')
            _save_sales_traffic_data(dt, reader)
        else:
            raise Exception(resp.content)


def calculate_average_usp():
    ninetydays = datetime.date.today() - datetime.timedelta(days=90)
    avgs = DetailPageSalesTraffic.objects.filter(dt__gte=ninetydays).values('child_asin').annotate(
        sum_session=Sum('sessions'), sum_units_ordered=Sum('units_ordered'))
    for i in avgs:
        asin = i['child_asin']
        sum_session = float(i['sum_session'])
        sum_units_ordered = float(i['sum_units_ordered'])
        avg = sum_units_ordered / sum_session * 100.0
        try:
            item = Item.objects.get(asin1=asin)
            item.avg_unit_session_percentage = avg
            item.save()
        except Item.DoesNotExist:
            pass


def check_avg_usp(dt):
    dpst = DetailPageSalesTraffic.objects.filter(dt=dt)
    for i in dpst:
        warning = []
        if i.unit_session_percentage < 10.0:
            warning.append('unit session percentage (%.2f%s) less than 10.0%s' % (i.unit_session_percentage, '%', '%'))
        try:
            item = Item.objects.get(asin1=i.child_asin)
            if i.unit_session_percentage < item.avg_unit_session_percentage:
                diff = item.avg_unit_session_percentage - i.unit_session_percentage
                if diff > 10.0:
                    warning.append(
                        'unit session percentage drops more than 10%s current is %.2f%s (the avg is %.2f%s)' % (
                        '%', i.unit_session_percentage, '%', item.avg_unit_session_percentage, '%'))
        except Item.DoesNotExist:
            pass
        if warning:
            warning_string = ','.join(warning)
            text = 'Unit Session Percentage Alert\n```Date:%s\nItem:%s\nItem Link:%s\nReason:%s```' % (
                dt, i.title, i.link, warning_string
            )
            _send_slack_dm('dev-dan-alerts', text)
