from django.conf.urls import url, include
from django.contrib import admin


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^auth/', include('loginsys.urls')),
    url(r'^profile/modify/$', 'web.views.profile_modify'),
    url(r'^profile/$', 'web.views.profile'),
    url(r'^product/$', 'web.views.product'),
    url(r'^upload_file/$', 'web.views.upload_file'),
    url(r'^', 'web.views.home'),
]


