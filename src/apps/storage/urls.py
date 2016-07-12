from django.conf.urls import url

from src.apps.storage.views import ProductJsonView, InvoiceCreate, ShipmentCreate, ShipmentDelete, ShipmentJsonView, \
    ProductAddView, ProductUpdateView, ProductStorageCreateView, ImportProductStorageView, InvoiceView

urlpatterns = [
    url(r'^product/add/$', view=ProductAddView.as_view(), name='product_add'),
    url(r'^product/(?P<pk>\d+)/change/$', view=ProductUpdateView.as_view(), name='product_edit'),
    url(r'^products/view/json/$', view=ProductJsonView.as_view(), name='products_json_view'),

    url(r'^productstorage/add/$', view=ProductStorageCreateView.as_view(), name='productstorage_add'),
    url(r'^productstorage/import/$', view=ImportProductStorageView.as_view(), name='productstorage_import'),

    url(r'^invoice/add/$', view=InvoiceCreate.as_view(), name='invoice_add'),
    url(r'^invoice/(?P<pk>\d+)/change/$', view=InvoiceView.as_view(), name='invoice_view'),

    url(r'^shipment/add/$', view=ShipmentCreate.as_view(), name='shipment_add'),
    url(r'^shipment/delete/$', view=ShipmentDelete.as_view(), name='shipment_delete'),
    url(r'^shipment/view/json/$', view=ShipmentJsonView.as_view(), name='shipment_json_view'),
]
