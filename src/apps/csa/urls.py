from django.conf.urls import url

from src.apps.csa.views import login_view, logout_view

urlpatterns = [
    url(r'^login/$', view=login_view, name='login_view'),
    url(r'^logout/$', view=logout_view, name='logout_view'),
]
