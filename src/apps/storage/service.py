from django.db import transaction

from src.apps.cashbox.serializer import FakeProductShipment
from src.apps.storage.models import ProductStorage, Product, Shipment, ProductKind, ProductGroup, ProductCategory
from src.apps.storage.serializer import FakeProductStorage, FakeProductKind

from src.common_helper import build_json_from_dict


UPDATE_STORAGE_DEC_TYPE = 0
UPDATE_STORAGE_INC_TYPE = 1

DEFAULT_PRODUCT_STORAGE_MIN_COUNT = 5


# Получить json представление фильтра для продуктов которые есть на складе - кол. > 0
def get_products_balance_json():

    storage = ProductStorage.objects.filter(product_count__gt=0)

    group_map = {}
    for item in storage:
        cur_product = item.product
        group = cur_product.product_kind.product_category.product_group.group_name
        category = cur_product.product_kind.product_category.category_name
        kind = cur_product.product_kind.kind_name

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
        product_list.append(FakeProductStorage(cur_product, **{'product_count': item.product_count}))

    return build_json_from_dict(group_map)


# Получить json представление фильтра для всех продуктов
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


# Получить json представление фильтра для добавления продукта
def get_kinds_for_product_add_json():

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


# Обновить количество товара на складе
def update_storage(product, update_type, count):

    storage = ProductStorage.objects.filter(product=product).first()
    if not storage:
        return
    if UPDATE_STORAGE_DEC_TYPE == update_type:
        storage.product_count -= count
    else:
        storage.product_count += count

    storage.save()


class StorageProductUpdater(object):

    def __init__(self, shipments):
        self.shipments = shipments
        self.shipment_kind_map = self.__aggregate_shipment_product()
        self.storage_kind_map = self.__aggregate_storage_product()

    # Структура для агрегирования товара
    class KindInfo(object):
        def __init__(self, kind_id, count, price):
            self.kind_id = kind_id
            self.count = count
            self.price = price

    # Аггрегирование пришедшего товара по видам
    def __aggregate_shipment_product(self):
        shipment_kind_map = {}
        for shipment in self.shipments:
            kind_id = shipment.product.product_kind.id
            kind_info = shipment_kind_map.get(kind_id)
            if not kind_info:
                kind_info = self.KindInfo(kind_id, shipment.product_count, shipment.cost_price)
                shipment_kind_map[kind_id] = kind_info
            else:
                kind_info.count += shipment.product_count
        return shipment_kind_map

    # Аггрегирование товара на складе по видам
    def __aggregate_storage_product(self):
        storage_kind_map = {}
        storage_products = ProductStorage.objects.all()

        for storage in storage_products:
            kind_id = storage.product.product_kind.id
            kind_info = storage_kind_map.get(kind_id)
            if not kind_info:
                kind_info = self.KindInfo(kind_id, storage.product_count, storage.product.cost_price)
                storage_kind_map[kind_id] = kind_info
            else:
                kind_info.count += storage.product_count
        return storage_kind_map

    # обновляется количество товара на складе
    def __update_storage_product_count(self):
        for shipment in self.shipments:
            storage = ProductStorage.objects.filter(product=shipment.product).first()
            if storage is None:
                storage = ProductStorage()
                storage.product = shipment.product,
                storage.min_count = DEFAULT_PRODUCT_STORAGE_MIN_COUNT
                storage.product_count = 0
            storage.product_count += shipment.product_count
            storage.save()

    # Вспомогательный метод для обновления стоимости товара
    @staticmethod
    def __update_product_cost_price_helper(storage_kind_info, shipment_kind_info):

        new_count = shipment_kind_info.count
        old_count = storage_kind_info.count
        new_price = shipment_kind_info.price
        old_price = storage_kind_info.price

        new_cost_price = (old_price * old_count + new_price * new_count) / (old_count + new_count)
        products = Product.objects.filter(product_kind=storage_kind_info.kind_id)
        if products:
            for product in products:
                product.cost_price = new_cost_price
                product.save()

    # Обновление стоимость товара
    def __update_product_cost_price(self):
        for kind_id, kind_info in self.shipment_kind_map.items():
            storage_kind_info = self.storage_kind_map.get(kind_id)
            if storage_kind_info:
                self.__update_product_cost_price_helper(storage_kind_info, kind_info)

    # обновить склад товара новыми партиями
    # обновляется количество товара на складе + обновляется себестоимость каждого продукта
    @transaction.atomic
    def update(self):
        self.__update_storage_product_count()
        self.__update_product_cost_price()


# Получить json представление партии товара по id
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
            price_wholesale=params[5],
            price_shop=params[6]
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
