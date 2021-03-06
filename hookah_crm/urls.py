"""hookah_crm URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static

from django.views.generic import RedirectView

from hookah_crm import settings

urlpatterns = [
    url(r'^$', RedirectView.as_view(url='admin/')),
    url(r'^csa/', include('src.apps.csa.urls')),
]

admin_override_urlpatterns = [
    url(r'^admin/logout/$', RedirectView.as_view(url='/csa/logout/')),
    url(r'^admin/login/$', RedirectView.as_view(url='/csa/login/')),

    url(r'^admin/cashbox/', include('src.apps.cashbox.urls')),
    url(r'^admin/storage/', include('src.apps.storage.urls')),
]

base_admin_urlpatterns = [
    url(r'^admin/', admin.site.urls),
]

urlpatterns += admin_override_urlpatterns
urlpatterns += base_admin_urlpatterns

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += staticfiles_urlpatterns()

# if settings.DEBUG:
#     import debug_toolbar
#     urlpatterns += [
#         url(r'^debug/', include(debug_toolbar.urls)),
#     ]
