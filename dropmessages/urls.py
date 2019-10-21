from django.conf.urls import include
from django.urls import path
from django.contrib import admin
from django.contrib.auth.views import auth_logout

from drop.views import no_resource, web_portal, web_register, RegisterUserView

from rest_framework_jwt.views import obtain_jwt_token, verify_jwt_token

urlpatterns = [
    path('', no_resource, name='no_resource'),
    path('admin/', admin.site.urls),

    # REST API FOR AUTHENTICATION TO GET JWT
    path('api/token/', obtain_jwt_token),
    path('api/verify/', verify_jwt_token),
    path('api/register/', RegisterUserView.as_view(), name='register'),

    # path('api/token/', TokenObtainPairView.as_view()),
    # path('api/token/refresh', TokenRefreshView.as_view()),
    # path('login/', user_login, name='user_login'),
    # path('logout/', user_logout, name='user_logout'),
    # path('logout/', auth_logout, name='logout'),

    # web portal for testing sockets
    path('web/portal/', web_portal, name='portal'),
    path('web/register/', web_register, name='register'),
    path('web/', include('django.contrib.auth.urls')),
]