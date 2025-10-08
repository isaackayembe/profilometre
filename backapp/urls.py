from django.urls import path
from . import views
from .views import (
    DeviceInstanceViewSet,
    DeviceModelViewSet,
    VenteViewSet,
    UserAdminViewSet,
    get_user_details,
    send_profilometre_lidar_data,
    ClientViewSet,
)

app_name = 'backapp'

urlpatterns = [
    # ---------------- AUTH ----------------
    path('api/auth/login/', views.login_view, name='api_login'),
    path('api/auth/signup/', views.signup_view, name='api_signup'),
    path('api/auth/logout/', views.logout_view, name='api_logout'),
    path('api/auth/profile/', views.user_profile, name='api_profile'),
    path('api/auth/change-password/', views.change_password, name='api_change_password'),

    # ✅ Vérification d’email et renvoi

    # ---------------- PASSWORD ----------------
    path('api/auth/password-reset/', views.password_reset_request, name='api_password_reset'),
    path('api/auth/password-reset-confirm/', views.password_reset_confirm, name='api_password_reset_confirm'),

    # ---------------- PROFILOMETRE / LIDAR ----------------
    path('profilometre-lidar/', send_profilometre_lidar_data, name='profilometre_lidar_post'),
    path('profilometre-lidar/list/', get_user_details, name='get_user_details'),

    # ---------------- VENDEUR ----------------
    path('api/vendeurs/modeles/', DeviceModelViewSet.as_view({'get': 'list', 'post': 'create'}), name='vendeur-modeles'),
    path('api/vendeurs/instances/', DeviceInstanceViewSet.as_view({'get': 'list', 'post': 'create'}), name='vendeur-instances'),
    path('api/vendeurs/instances/<int:pk>/assign/', DeviceInstanceViewSet.as_view({'post': 'assign_client'}), name='vendeur-instance-assign'),

    path('api/vendeurs/ventes/', VenteViewSet.as_view({'get': 'list', 'post': 'create'}), name='vendeur-ventes'),
    path('api/vendeurs/clients/', ClientViewSet.as_view({'get': 'list'}), name='vendeur-clients'),
    path('api/vendeurs/clients/update/', ClientViewSet.as_view({'post': 'update_by_email'}), name='vendeur-client-update'),

    # ---------------- ADMIN ----------------
    path('api/admin/utilisateurs/', UserAdminViewSet.as_view({'get': 'list', 'post': 'create'}), name='admin-users'),
    path('api/admin/utilisateurs/<int:pk>/', UserAdminViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='admin-users-detail'),
]
