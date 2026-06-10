from django.urls import path
from . import api_views
from rest_framework_simplejwt.views import TokenRefreshView

app_name = 'api-users'

urlpatterns = [
    path('register/', api_views.RegisterAPIView.as_view(), name='register'),
    path('login/', api_views.LoginAPIView.as_view(), name='login'),
    path('logout/', api_views.LogoutAPIView.as_view(), name='logout'),
    path('profile/', api_views.ProfileAPIView.as_view(), name='profile'),
    path('change-password/', api_views.ChangePasswordAPIView.as_view(), name='change-password'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
]
