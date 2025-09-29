from django.urls import path, include
from . import views
from .views import DeviceModelViewSet, StockViewSet, SaleViewSet, list_profilometre_lidar_data, send_profilometre_lidar_data

app_name = 'backapp'

urlpatterns = [
    # Authentication endpoints sécurisés avec allauth
    path('api/auth/login/', views.login_view, name='api_login'),
    path('api/auth/signup/', views.signup_view, name='api_signup'),
    path('api/auth/logout/', views.logout_view, name='api_logout'),
    path('api/auth/profile/', views.user_profile, name='api_profile'),
    path('api/auth/password-reset/', views.password_reset_request, name='api_password_reset'),
    path('api/auth/password-reset-confirm/', views.password_reset_confirm, name='api_password_reset_confirm'),
    
    # Nouveaux endpoints allauth
    path('api/auth/email-verify/', views.email_verification, name='api_email_verify'),
    path('api/auth/email-resend/', views.resend_email_verification, name='api_email_resend'),
    path('api/auth/session-info/', views.session_info, name='api_session_info'),
    path('api/auth/change-password/', views.change_password, name='api_change_password'),
    
    # IoT Data endpoints - Une seule API flexible pour tous les capteurs
    path('profilometre-lidar/', send_profilometre_lidar_data, name='profilometre_lidar_post'),
    path('profilometre-lidar/list/', list_profilometre_lidar_data, name='profilometre_lidar_list'),

    path('api/modeles/', DeviceModelViewSet.as_view({'get': 'list', 'post': 'create'}), name='device-model-list'),
    path('api/modeles/<int:pk>/', DeviceModelViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='device-model-detail'),
    path('api/stocks/', StockViewSet.as_view({'get': 'list', 'post': 'create'}), name='stock-list'),
    path('api/stocks/<int:pk>/', StockViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='stock-detail'),
    path('api/ventes/', SaleViewSet.as_view({'get': 'list', 'post': 'create'}), name='sale-list'),
    path('api/ventes/<int:pk>/', SaleViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='sale-detail'),
]