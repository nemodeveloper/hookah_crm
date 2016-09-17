from django.conf.urls import url
from django.views.generic import RedirectView

from src.apps.cashbox.views import ProductSellCreate, ProductShipmentCreate, ProductShipmentJsonView, \
    ProductShipmentDelete, PaymentTypeCreate, PaymentTypeDelete, PaymentTypeJsonView, CashTakeCreateView, CashTakeView, \
    ProductSellView, ProductSellEmployerReport, ProductSellDeleteView

urlpatterns = [
    url(r'^productsell/add/$', view=ProductSellCreate.as_view(), name='product_sell_add'),
    url(r'^productsell/(?P<pk>\d+)/view/$', view=ProductSellView.as_view(), name='product_sell_view'),
    url(r'^productsell/(?P<pk>\d+)/change/$', view=RedirectView.as_view(pattern_name='product_sell_view')),
    url(r'^productsell/(?P<pk>\d+)/delete/$', view=ProductSellDeleteView.as_view(), name='product_sell_delete_view'),

    url(r'^productsell/report/employer/(?P<pk>\d+)/$', view=ProductSellEmployerReport.as_view(), name="product_sell_employer_report_view"),

    url(r'^productshipment/add/$', view=ProductShipmentCreate.as_view(), name='product_shipment_add'),
    url(r'^productshipment/delete/$', view=ProductShipmentDelete.as_view(), name='product_shipment_delete'),
    url(r'^productshipment/view/json/$', view=ProductShipmentJsonView.as_view(), name='product_shipment_json_view'),

    url(r'^paymenttype/add/$', view=PaymentTypeCreate.as_view(), name='payment_type_add'),
    url(r'^paymenttype/delete/$', view=PaymentTypeDelete.as_view(), name='payment_type_delete'),
    url(r'^paymenttype/view/json/$', view=PaymentTypeJsonView.as_view(), name='payment_type_json_view'),

    url(r'^cashtake/add/$', view=CashTakeCreateView.as_view(), name='cash_take_add'),
    url(r'^cashtake/(?P<pk>\d+)/view/$', view=CashTakeView.as_view(), name='cash_take_view'),
    url(r'^cashtake/(?P<pk>\d+)/change/$', view=RedirectView.as_view(pattern_name='cash_take_view')),
    url(r'^cashtake/(?P<pk>\d+)/delete/$', view=RedirectView.as_view(pattern_name='cash_take_view')),
]
