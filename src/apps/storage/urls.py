from django.conf.urls import url

from src.apps.storage.views import ProductJsonView, InvoiceCreate, ShipmentCreate, ShipmentDelete, ShipmentJsonView

urlpatterns = [
    url(r'^products/view/json/$', view=ProductJsonView.as_view(), name='products_json_view'),

    url(r'^invoice/add/$', view=InvoiceCreate.as_view(), name='invoice_add'),

    url(r'^shipment/add/$', view=ShipmentCreate.as_view(), name='shipment_add'),
    url(r'^shipment/delete/$', view=ShipmentDelete.as_view(), name='shipment_delete'),
    url(r'^shipment/view/json/$', view=ShipmentJsonView.as_view(), name='shipment_json_view'),
]
