from django.conf.urls import url
from django.views.generic import RedirectView

from src.apps.storage.views import ProductJsonView, InvoiceCreate, ShipmentCreate, ShipmentDelete, ShipmentJsonView, \
    ProductAddViewMixin, ProductUpdateViewMixin, ImportProductViewMixin, InvoiceUpdateView, InvoiceBuyReport, \
    ExportProductViewMixin, ProductView, ReviseAddView, ReviseAcceptView, ReviseDeleteView, ReviseChangeView, \
    DumpDBView, InvoiceDeleteView

urlpatterns = [
    url(r'^product/add/$', view=ProductAddViewMixin.as_view(), name='product_add'),
    url(r'^product/(?P<pk>\d+)/change/$', view=ProductUpdateViewMixin.as_view(), name='product_edit'),
    url(r'^product/(?P<pk>\d+)/view/$', view=ProductView.as_view(), name='product_view'),
    url(r'^product/view/json/$', view=ProductJsonView.as_view(), name='product_json_view'),
    url(r'^product/import/$', view=ImportProductViewMixin.as_view(), name='product_import'),
    url(r'^product/export/$', view=ExportProductViewMixin.as_view(), name='product_export'),

    url(r'^system/dump/db$', view=DumpDBView.as_view(), name='system_dump_db_view'),

    url(r'^revise/add/$', view=ReviseAddView.as_view(), name='revise_add_view'),
    url(r'^revise/(?P<pk>\d+)/change/$', view=ReviseChangeView.as_view(), name='revise_change_view'),
    url(r'^revise/(?P<pk>\d+)/accept/$', view=ReviseAcceptView.as_view(), name='revise_accept_view'),
    url(r'^revise/(?P<pk>\d+)/delete/$', view=ReviseDeleteView.as_view(), name='revise_delete_view'),

    url(r'^invoice/add/$', view=InvoiceCreate.as_view(), name='invoice_add'),
    url(r'^invoice/(?P<pk>\d+)/view/$', view=InvoiceUpdateView.as_view(), name='invoice_view'),
    url(r'^invoice/(?P<pk>\d+)/change/$', view=RedirectView.as_view(pattern_name='invoice_view')),
    url(r'^invoice/(?P<pk>\d+)/delete/$', view=InvoiceDeleteView.as_view(), name='invoice_delete'),
    url(r'^invoice/report/$', view=InvoiceBuyReport.as_view(), name='invoice_buy_report'),

    url(r'^shipment/add/$', view=ShipmentCreate.as_view(), name='shipment_add'),
    url(r'^shipment/delete/$', view=ShipmentDelete.as_view(), name='shipment_delete'),
    url(r'^shipment/view/json/$', view=ShipmentJsonView.as_view(), name='shipment_json_view'),
]
