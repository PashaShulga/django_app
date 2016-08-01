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
    # url(r'^add_column/$', add_column),
    url(r'^summernote/', include('django_summernote.urls')),

    url(r'^product/(?P<page_slug>[\w-]+)/$', product),
    url(r'^product/(?P<page_slug>[\w-]+)/update/$', product_update),
    url(r'^product/(?P<page_slug>[\w-]+)/delete/$', product_delete),
    url(r'^product/(?P<page_slug>[\w-]+)/insert/$', product_insert),
    url(r'^product/(?P<page_slug>[\w-]+)/delete_all/$', delete_all),

    url(r'^edit_company/modify$', modify_company),
    url(r'^list_company/change/(?P<id>([0-9]+))/$', list_company_change),
    url(r'^list_company/change/(?P<company_id>([0-9]+))/delete/(?P<chart_id>([0-9]+))', chart_delete),
    url(r'^list_company/change/(?P<page_slug>[\w-]+)/delete_table/$', delete_table),
    url(r'^list_company/$', list_company),
    url(r'^list_company/get_table_columns/$', get_table_columns_ajax),
    url(r'^data_analytics/$', data_analytics),
    url(r'^company/users/$', company_users),
    url(r'^company/delete/$', company_delete_user),
    url(r'^company/add/$', add_new_company),
    url(r'^docs/', documentation),

    url(r'^', home),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


