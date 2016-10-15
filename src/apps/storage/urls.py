from django.conf.urls import url
from django.views.generic import RedirectView

from src.apps.storage.views import ProductJsonView, InvoiceCreate, ShipmentCreate, ShipmentDelete, ShipmentJsonView, \
    ProductAddViewMixin, ProductUpdateViewMixin, ImportProductViewMixin, InvoiceView, InvoiceBuyReport, \
    ExportProductViewMixin

urlpatterns = [
    url(r'^product/add/$', view=ProductAddViewMixin.as_view(), name='product_add'),
    url(r'^product/(?P<pk>\d+)/change/$', view=ProductUpdateViewMixin.as_view(), name='product_edit'),
    url(r'^product/view/json/$', view=ProductJsonView.as_view(), name='product_json_view'),
    url(r'^product/import/$', view=ImportProductViewMixin.as_view(), name='product_import'),
    url(r'^product/export/$', view=ExportProductViewMixin.as_view(), name='product_export'),

    url(r'^invoice/add/$', view=InvoiceCreate.as_view(), name='invoice_add'),
    url(r'^invoice/(?P<pk>\d+)/view/$', view=InvoiceView.as_view(), name='invoice_view'),
    url(r'^invoice/(?P<pk>\d+)/change/$', view=RedirectView.as_view(pattern_name='invoice_view')),
    url(r'^invoice/(?P<pk>\d+)/delete/$', view=RedirectView.as_view(pattern_name='invoice_view')),
    url(r'^invoice/report/$', view=InvoiceBuyReport.as_view(), name='invoice_buy_report'),

    url(r'^shipment/add/$', view=ShipmentCreate.as_view(), name='shipment_add'),
    url(r'^shipment/delete/$', view=ShipmentDelete.as_view(), name='shipment_delete'),
    url(r'^shipment/view/json/$', view=ShipmentJsonView.as_view(), name='shipment_json_view'),
]
