from src.apps.cashbox.helper import FakeProductShipment
from src.apps.storage.models import ProductStorage, Product, Shipment, ProductKind, ProductGroup, ProductCategory
from src.apps.storage.serializer import FakeProductStorage, FakeProductKind

from src.common_helper import build_json_from_dict


UPDATE_STORAGE_DEC_TYPE = 0
UPDATE_STORAGE_INC_TYPE = 1

DEFAULT_PRODUCT_STORAGE_MIN_COUNT = 2


def get_products_balance_json():

    storage = ProductStorage.objects.filter(product_count__gt=0)

    category_map = {}
    for item in storage:
        cur_product = item.product
        group = cur_product.product_kind.product_category.product_group.group_name
        category = cur_product.product_kind.product_category.category_name
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

    group_map = {}
    for product in products:
        group = product.product_kind.product_category.product_group.group_name
        category = product.product_kind.product_category.category_name
        kind = product.product_kind.kind_name

        category_map = group_map.get(group)
        if not category_map:
            category_map = {}
            group_map[group] = category_map

        kind_map = category_map.get(category)
        if not kind_map:
            kind_map = {}
            category_map[category] = kind_map

        product_list = kind_map.get(kind)
        if not product_list:
            product_list = []
            kind_map[kind] = product_list
        product_list.append({'id': product.id, 'product_name': product.product_name})

    return build_json_from_dict(group_map)


def get_kinds_for_product_add():

    kinds = ProductKind.objects.all()
    group_map = {}

    for kind in kinds:
        group = kind.product_category.product_group.group_name
        category = kind.product_category.category_name

        category_map = group_map.get(group)
        if not category_map:
            category_map = {}
            group_map[group] = category_map

        kind_list = category_map.get(category)
        if not kind_list:
            kind_list = []
            category_map[category] = kind_list

        kind_list.append(FakeProductKind(kind, **{'category': category, 'group': group}))

    return build_json_from_dict(group_map)


# Обновить товар на складе
def update_storage(product, update_type, count):

    storage = ProductStorage.objects.filter(product=product).first()
    if not storage:
        return
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


# Получить или создать группу товара по имени
def get_or_create_group(name):

    group = ProductGroup.objects.filter(group_name=name).first()
    if not group:
        group = ProductGroup(group_name=name)
        group.save()
    return group


# Получить или создать категорию товара по имени
def get_or_create_category(name, group):

    category = ProductCategory.objects.filter(category_name=name).first()
    if not category:
        category = ProductCategory(category_name=name, product_group=group)
        category.save()
    return category


# Получить или создать вид товара по имени
def get_or_create_kind(name, category):

    kind = ProductKind.objects.filter(kind_name=name).first()
    if not kind:
        kind = ProductKind(kind_name=name, product_category=category)
        kind.save()
    return kind


# Получить или создать товар
def get_or_create_product(kind, params):

    product = Product.objects.filter(product_name=params[0]).first()
    if not product:
        product = Product(
            product_kind=kind,
            product_name=params[0],
            product_code=params[1],
            cost_price=params[2],
            price_retail=params[3],
            price_discount=params[4],
            price_wholesale=params[5]
        )
        product.save()

    return product


# Обновить или добавить товар на склад
def add_or_update_product_storage(product, params):

    storage = ProductStorage.objects.filter(product=product).first()
    if not storage:
        storage = ProductStorage(
            product=product,
            product_count=params[0],
            min_count=params[1]
        )
    else:
        storage.product_count = params[0]
        storage.min_count = params[1]

    storage.save()