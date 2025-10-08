from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from django.db import models
from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied

# ---------------------------------------------------------
# 1️⃣ Création des permissions personnalisées pour les vendeurs
# ---------------------------------------------------------
def create_vendor_permissions():
    """
    Crée les permissions personnalisées pour les vendeurs dans la base.
    À exécuter une seule fois ou lors d'un migration/script.
    """
    vendor_permissions = [
        ('view_user_devices', 'Peut voir les profilomètres des utilisateurs'),
        ('configure_user_devices', 'Peut configurer les profilomètres des utilisateurs'),
        ('resolve_device_issues', 'Peut résoudre les problèmes des profilomètres'),
        ('manage_own_stock', 'Peut gérer son propre stock'),
        ('view_own_sales', 'Peut voir ses propres ventes'),
        ('create_device_models', 'Peut créer des modèles de profilomètres'),
        ('view_own_vendor_data', 'Peut voir uniquement ses propres données de vendeur'),
    ]

    content_type = ContentType.objects.get_for_model(models.Model)  # générique
    for codename, name in vendor_permissions:
        Permission.objects.get_or_create(
            codename=codename,
            name=name,
            content_type=content_type,
        )


# ---------------------------------------------------------
# 2️⃣ Mixin pour vérifier les permissions d'un vendeur
# ---------------------------------------------------------
class VendorPermissionsMixin:
    """Mixin pour vérifier facilement les permissions vendeur"""

    def can_view_user_device(self, user, device=None):
        return user.has_perm('backapp.view_user_devices')

    def can_configure_user_device(self, user, device=None):
        return user.has_perm('backapp.configure_user_devices')

    def can_resolve_device_issues(self, user, device=None):
        return user.has_perm('backapp.resolve_device_issues')

    def can_manage_own_stock(self, user, vendor):
        if user.has_perm('backapp.manage_own_stock'):
            return hasattr(user, 'vendeur_profile') and user.vendeur_profile == vendor
        return False

    def can_view_own_sales(self, user):
        return user.has_perm('backapp.view_own_sales')

    def can_create_device_models(self, user):
        return user.has_perm('backapp.create_device_models')


# ---------------------------------------------------------
# 3️⃣ Classes de permission DRF
# ---------------------------------------------------------
class IsVendeur(permissions.BasePermission):
    """
    Vérifie que l'utilisateur est un vendeur (is_staff=True) et a au moins un profil VendeurProfile
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            hasattr(request.user, 'vendeur_profile')
        )

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'vendeur'):
            return obj.vendeur.user == request.user
        return True


class IsClient(permissions.BasePermission):
    """
    Vérifie que l'utilisateur est un client normal (is_staff=False) et a un ClientProfile
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            hasattr(request.user, 'client_profile')
        )

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'client'):
            return obj.client == request.user
        return True


class IsSuperUser(permissions.BasePermission):
    """
    Vérifie que l'utilisateur est superuser (accès complet)
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser

    def has_object_permission(self, request, view, obj):
        return True


# ---------------------------------------------------------
# 4️⃣ Listes de permissions prédéfinies
# ---------------------------------------------------------
# Pour l'admin (superuser)
VENDOR_ADMIN_PERMISSIONS = [
    'add_vendor',
    'change_vendor',
    'delete_vendor',
    'view_vendor',
    'add_devicemodel',
    'change_devicemodel',
    'delete_devicemodel',
    'view_devicemodel',
    'add_stock',
    'change_stock',
    'delete_stock',
    'view_stock',
    'add_sale',
    'change_sale',
    'delete_sale',
    'view_sale',
    'add_deviceconfiguration',
    'change_deviceconfiguration',
    'delete_deviceconfiguration',
    'view_deviceconfiguration',
]

# Pour un vendeur normal (accès limité)
VENDOR_USER_PERMISSIONS = [
    'view_user_devices',
    'configure_user_devices',
    'resolve_device_issues',
    'manage_own_stock',
    'view_own_sales',
    'create_device_models',
    'view_own_vendor_data',
]
from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission pour que seul le propriétaire d’un objet puisse le modifier,
    mais tout le monde peut lire.
    """

    def has_object_permission(self, request, view, obj):
        # Les méthodes GET, HEAD, OPTIONS sont toujours autorisées
        if request.method in permissions.SAFE_METHODS:
            return True

        # Vérifie si l'objet a un attribut `user` ou `owner`
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'owner'):
            return obj.owner == request.user

        return False

