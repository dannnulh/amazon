import StringIO
import csv
from time import sleep
from mws import mws

from .models import Item


def _get_float(value, default=None):
    result = default
    try:
        result = float(value)
    except:
        pass
    return result


def _get_int(value, default=None):
    result = default
    try:
        result = int(value)
    except:
        pass
    return result


def _decode(value):
    print '----------'
    print value
    return value.decode('utf-8', errors='ignore')


def get_amazon_data():
    x = mws.Reports(access_key='AKIAIJBJ3KDB22JYZTHA', secret_key='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',
                    account_id='A1B4GJWW9XJ35M', region='UK')

    resp = x.request_report(report_type='_GET_MERCHANT_LISTINGS_ALL_DATA_')
    request_id = resp.parsed.ReportRequestInfo.ReportRequestId
    sleep(30)

    resp = x.get_report_request_list(requestids=(request_id,))
    report_id = resp.parsed.ReportRequestInfo.GeneratedReportId

    resp = x.get_report(report_id=report_id)
    csv_string = resp.parsed

    f = StringIO.StringIO(csv_string)
    reader = csv.reader(f, delimiter='\t')
    with open('report.csv', 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        for row in reader:
            writer.writerow(row)


def save_amazon_data():
    f = open('report.csv', 'rb')
    reader = csv.reader(f)
    for row in reader:
        row = map(_decode, row)
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
