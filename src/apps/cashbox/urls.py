from django.conf.urls import url

from src.apps.cashbox.views import ProductSellCreate, ProductShipmentCreate, ProductShipmentJsonView, \
    ProductShipmentDelete, PaymentTypeCreate, PaymentTypeDelete, PaymentTypeJsonView

urlpatterns = [
    url(r'^productsell/add/$', view=ProductSellCreate.as_view(), name='product_sell_add'),

    url(r'^productshipment/add/$', view=ProductShipmentCreate.as_view(), name='product_shipment_add'),
    url(r'^productshipment/delete/$', view=ProductShipmentDelete.as_view(), name='product_shipment_delete'),
    url(r'^productshipment/view/json/$', view=ProductShipmentJsonView.as_view(), name='product_shipment_json_view'),

    url(r'^paymenttype/add/$', view=PaymentTypeCreate.as_view(), name='payment_type_add'),
    url(r'^paymenttype/delete/$', view=PaymentTypeDelete.as_view(), name='payment_type_delete'),
    url(r'^paymenttype/view/json/$', view=PaymentTypeJsonView.as_view(), name='payment_type_json_view'),
]
