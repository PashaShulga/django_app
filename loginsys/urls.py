from django.conf.urls import url
from loginsys.views import *


urlpatterns = [
    url(r'registration/', registration),
    url(r'login/', LoginUser.as_view(), name='login_user'),
    url(r'logout/', logout),
    url(r'^account/reset_password_confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        PasswordResetConfirmView.as_view(), name='reset_password_confirm'),
                       # PS: url above is going to used for next section of implementation.
    url(r'^account/reset_password', ResetPasswordRequestView.as_view(), name="reset_password"),
]