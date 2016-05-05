from django.conf.urls import url, include
from django.contrib import admin
from web.views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^auth/', include('loginsys.urls')),
    url(r'^api/', include('api.urls')),

    url(r'^profile/modify/$', profile_modify),
    url(r'^profile/$', profile),
    url(r'^product/$', product),
    url(r'^add_column/$', add_column),
    url(r'^product/update$', product_update),
    url(r'^product/delete$', product_delete),
    url(r'^product/insert$', product_insert),
    url(r'^edit_company/modify$', modify_company),
    url(r'^list_company/$', list_company),
    url(r'^data_analytics/$', data_analytics),
    url(r'^', home),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


