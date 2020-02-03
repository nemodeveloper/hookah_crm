from django.conf.urls import url
from django.views.generic import RedirectView

from src.apps.cashbox.views import ProductSellCreate, ProductShipmentCreate, ProductShipmentJsonView, \
    ProductShipmentDelete, PaymentTypeCreate, PaymentTypeDelete, PaymentTypeJsonView, \
    ProductSellUpdateView, ProductSellEmployerReport, ProductSellDeleteView, ProductSellReport, \
    ProductSellCreditReportView, ProductSellProfitReportView, ProductShipmentUpdate, ProductSellCheckView

urlpatterns = [
    url(r'^productsell/add/$', view=ProductSellCreate.as_view(), name='product_sell_add'),
    url(r'^productsell/(?P<pk>\d+)/view/$', view=ProductSellUpdateView.as_view(), name='product_sell_view'),
    url(r'^productsell/(?P<pk>\d+)/change/$', view=RedirectView.as_view(pattern_name='product_sell_view'), name='product_update_view'),
    url(r'^productsell/(?P<pk>\d+)/delete/$', view=ProductSellDeleteView.as_view(), name='product_sell_delete_view'),
    url(r'^productsell/(?P<id>\d+)/check/$', view=ProductSellCheckView.as_view(), name='product_sell_check_view'),

    url(r'^productsell/report/employer/(?P<pk>\d+)/$', view=ProductSellEmployerReport.as_view(), name='product_sell_employer_report_view'),
    url(r'^productsell/report/(?P<pk>\d+)/$', view=ProductSellReport.as_view(), name='product_sell_report_view'),
    url(r'^productsell/report/credit/$', view=ProductSellCreditReportView.as_view(), name='product_sell_report_credit_view'),
    url(r'^productsell/report/profit/$', view=ProductSellProfitReportView.as_view(), name='product_sell_report_profit_view'),

    url(r'^productshipment/add/$', view=ProductShipmentCreate.as_view(), name='product_shipment_add'),
    url(r'^productshipment/(?P<pk>\d+)/change/$', view=ProductShipmentUpdate.as_view(), name='product_shipment_update'),
    url(r'^productshipment/delete/$', view=ProductShipmentDelete.as_view(), name='product_shipment_delete'),
    url(r'^productshipment/view/json/$', view=ProductShipmentJsonView.as_view(), name='product_shipment_json_view'),

    url(r'^paymenttype/add/$', view=PaymentTypeCreate.as_view(), name='payment_type_add'),
    url(r'^paymenttype/delete/$', view=PaymentTypeDelete.as_view(), name='payment_type_delete'),
    url(r'^paymenttype/view/json/$', view=PaymentTypeJsonView.as_view(), name='payment_type_json_view'),
]
