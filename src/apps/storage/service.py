from src.apps.cashbox.helper import FakeProductShipment
from src.apps.storage.models import ProductStorage, Product, Shipment
from src.apps.storage.helper import FakeProductStorage

from src.common_helper import build_json_from_dict


UPDATE_STORAGE_DEC_TYPE = 0
UPDATE_STORAGE_INC_TYPE = 1

DEFAULT_PRODUCT_STORAGE_MIN_COUNT = 2


def get_products_balance_json():

    storage = ProductStorage.objects.filter(product_count__gt=0)

    category_map = {}
    for item in storage:
        cur_product = item.product
        category = cur_product.product_category.category_name
        kind = cur_product.product_kind.kind_name

        kind_map = category_map.get(category)
        if not kind_map:
            kind_map = {}
            category_map[category] = kind_map

        product_list = kind_map.get(kind)
        if not product_list:
            product_list = []
            kind_map[kind] = product_list
        product_list.append(FakeProductStorage(cur_product, **{'product_count': item.product_count}))

    return build_json_from_dict(category_map)


def get_products_all_json():

    products = Product.objects.all()

    category_map = {}
    for product in products:
        category = product.product_category.category_name
        kind = product.product_kind.kind_name

        kind_map = category_map.get(category)
        if not kind_map:
            kind_map = {}
            category_map[category] = kind_map

        product_list = kind_map.get(kind)
        if not product_list:
            product_list = []
            kind_map[kind] = product_list
        product_list.append(FakeProductStorage(product))

    return build_json_from_dict(category_map)


def update_storage(product_id, update_type, count):

    storage = ProductStorage.objects.get(product=product_id)
    if UPDATE_STORAGE_DEC_TYPE == update_type:
        storage.product_count -= count
    else:
        storage.product_count += count

    storage.save()


def update_storage_by_shipments(shipments):

    for shipment in shipments:
        storage = ProductStorage.objects.filter(product=shipment.product).first()
        if storage is None:
            storage = ProductStorage()
            storage.product = shipment.product,
            storage.min_count = DEFAULT_PRODUCT_STORAGE_MIN_COUNT
            storage.product_count = 0
        storage.product_count += shipment.product_count
        storage.save()


def get_shipment_json(id):

    shipment = Shipment.objects.get(id=id)
    return build_json_from_dict(FakeProductShipment(shipment))






