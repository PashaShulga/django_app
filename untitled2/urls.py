from django.conf.urls import url, include
from django.contrib import admin
from web.views import *

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^auth/', include('loginsys.urls')),
    url(r'^profile/modify/$', profile_modify),
    url(r'^profile/$', profile),
    url(r'^product/$', product),
    # url(r'^upload_file/$', 'web.views.upload_file'),
    url(r'^', home),
]


