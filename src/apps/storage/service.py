import logging
import operator

from django.db import transaction

from src.apps.cashbox.serializer import FakeProductShipment
from src.apps.storage.models import Product, Shipment, ProductKind, ProductGroup, ProductCategory
from src.apps.storage.serializer import FakeProduct, FakeProductKind

from src.common_helper import build_json_from_dict

UPDATE_STORAGE_DEC_TYPE = 0
UPDATE_STORAGE_INC_TYPE = 1

DEFAULT_PRODUCT_STORAGE_MIN_COUNT = 5


cashbox_log = logging.getLogger('storage_log')


def aggr_product_kinds():

    kinds = ProductKind.objects.select_related().all()
    aggr_kind_map = {kind.id: [kind.kind_name, kind.product_category.category_name, kind.product_category.product_group.group_name] for kind in kinds}

    return aggr_kind_map


# Получить json представление фильтра для продуктов которые есть на складе - кол. > 0
def get_products_balance_json():

    aggr_kind_map = aggr_product_kinds()
    products = Product.objects.raw('SELECT * FROM storage_product WHERE product_count > 0')
    group_map = {}

    for product in products:
        product_kind = aggr_kind_map.get(product.product_kind_id)

        group = product_kind[2]
        category = product_kind[1]
        kind = product_kind[0]

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
        product_list.append(FakeProduct(product,
                                        **{'product_group': group,
                                           'product_category': category, 'product_kind': kind}))
    return build_json_from_dict(group_map)


# Получить json представление фильтра для всех продуктов
def get_products_all_json():
    aggr_kind_map = aggr_product_kinds()
    products = Product.objects.raw('SELECT * FROM storage_product')

    group_map = {}
    for product in products:
        product_kind = aggr_kind_map[product.product_kind_id]
        group = product_kind[2]
        category = product_kind[1]
        kind = product_kind[0]

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
    kinds = ProductKind.objects.select_related().all()
    return serialize_kinds(kinds)


def get_kinds_for_export_json(export_type):

    if export_type == 'wholesale':
        ids = Product.objects.values_list('product_kind_id').filter(product_count__gt=0).distinct()
    elif export_type == 'revise':
        ids = Product.objects.values_list('product_kind_id').distinct()
    else:
        raise ValueError('Неверный тип выгрузки видов товара - %s' % export_type)
    kinds = ProductKind.objects.select_related().filter(id__in=ids)

    return serialize_kinds(kinds)


def serialize_kinds(kinds):
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

    # отсортируем на сервере
    for category in group_map.values():
        for key in category.keys():
            category[key] = sorted(category[key], key=operator.attrgetter('kind_name'))

    return build_json_from_dict(group_map)


class StorageProductUpdater(object):
    def __init__(self, shipments):
        self.shipments = shipments
        self.single_shipments = []
        self.aggr_shipment_kind_map = self.__aggregate_shipment_product()
        self.aggr_storage_kind_map = self.__aggregate_products()

    # Структура для агрегирования товара
    class KindInfo(object):
        def __init__(self, kind_id, count, price):
            self.kind_id = kind_id
            self.count = count
            self.price = price

    # Аггрегирование пришедшего товара по видам для обновления стоимости
    # берем только те которые разрешено аггрегировать
    # остальное обновляем еденично, каждый товар
    def __aggregate_shipment_product(self):
        shipment_kind_map = {}
        for shipment in self.shipments:
            if not shipment.product.product_kind.need_update_products:
                self.single_shipments.append(shipment)
            else:
                kind_id = shipment.product.product_kind.id
                kind_info = shipment_kind_map.get(kind_id)
                if not kind_info:
                    kind_info = self.KindInfo(kind_id, shipment.product_count,
                                              shipment.cost_price * shipment.product_count)
                    shipment_kind_map[kind_id] = kind_info
                else:
                    kind_info.price += shipment.cost_price * shipment.product_count
                    kind_info.count += shipment.product_count
        return shipment_kind_map

    # Аггрегирование товара на складе по видам
    # берем только те которые разрешено аггрегировать
    def __aggregate_products(self):
        storage_kind_map = {}
        products = Product.objects.select_related().filter(product_kind__need_update_products=True)

        for product in products:
            kind_id = product.product_kind.id
            kind_info = storage_kind_map.get(kind_id)
            if not kind_info:
                kind_info = self.KindInfo(kind_id, product.product_count, product.cost_price * product.product_count)
                storage_kind_map[kind_id] = kind_info
            else:
                kind_info.price += product.cost_price * product.product_count
                kind_info.count += product.product_count
        return storage_kind_map

    # обновляется количество товара на складе
    def __update_products_count(self):
        for shipment in self.shipments:
            product = Product.objects.get(id=shipment.product.id)
            product.product_count += shipment.product_count
            product.save()

    # Вспомогательный метод для обновления стоимости товара
    @staticmethod
    def __update_product_cost_price_helper(storage_kind_info, shipment_kind_info):

        new_count = shipment_kind_info.count
        old_count = storage_kind_info.count
        new_price = shipment_kind_info.price
        old_price = storage_kind_info.price

        new_cost_price = (old_price + new_price) / (old_count + new_count)
        Product.objects.filter(product_kind=storage_kind_info.kind_id).update(cost_price=new_cost_price)

    # Обновление стоимость товара
    def __update_product_cost_price(self):
        for kind_id, kind_info in self.aggr_shipment_kind_map.items():
            storage_kind_info = self.aggr_storage_kind_map.get(kind_id)
            if storage_kind_info:
                self.__update_product_cost_price_helper(storage_kind_info, kind_info)

    @staticmethod
    def __update_single_product(product, shipment):

        new_count = shipment.product_count
        old_count = product.product_count - new_count

        new_cost = shipment.cost_price
        old_price = product.cost_price

        product.cost_price = (old_count * old_price + new_count * new_cost) / product.product_count
        product.save()

    # Обновить стоимость еденичных товаров
    def __update_single_products(self):
        for shipment in self.single_shipments:
            product = Product.objects.get(id=shipment.product.id)
            StorageProductUpdater.__update_single_product(product, shipment)

    # обновить склад товара новыми партиями
    # обновляется количество товара на складе + обновляется себестоимость каждого продукта
    @transaction.atomic
    def update(self):
        self.__update_products_count()
        self.__update_product_cost_price()
        self.__update_single_products()


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
    category = ProductCategory.objects.filter(category_name=name, product_group=group).first()
    if not category:
        category = ProductCategory(category_name=name, product_group=group)
        category.save()
    return category


# Получить или создать вид товара по имени
def get_or_create_kind(name, category):
    kind = ProductKind.objects.filter(kind_name=name, product_category=category).first()
    if not kind:
        kind = ProductKind(kind_name=name, product_category=category)
        kind.save()
    return kind


# Обновить или создать товар
def update_or_create_product(kind, params):
    product = Product.objects.filter(product_kind=kind, product_name=params[0]).first()
    if not product:
        product = Product(
            product_kind=kind,
            product_name=params[0],
            cost_price=params[1],
            price_retail=params[2],
            price_discount=params[3],
            price_shop=params[4],
            price_wholesale=params[5],
            product_count=params[6],
            min_count=params[7]
        )
    else:
        product.product_kind = kind
        product.product_name = params[0]
        product.cost_price = params[1]
        product.price_retail = params[2]
        product.price_discount = params[3]
        product.price_shop = params[4]
        product.price_wholesale = params[5]
        product.product_count = params[6]
        product.min_count = params[7]

    product.save()
    return product


def update_all_product_cost_by_kind(product):
    with transaction.atomic():
        Product.objects.filter(product_kind=product.product_kind) \
            .update(cost_price=product.cost_price,
                    price_retail=product.price_retail,
                    price_discount=product.price_discount,
                    price_wholesale=product.price_wholesale,
                    price_shop=product.price_shop)
