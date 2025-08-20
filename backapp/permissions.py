from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db import models

def create_vendor_permissions():
    """Créer les permissions personnalisées pour les vendeurs"""
    
    # Permissions pour les vendeurs
    vendor_permissions = [
        # Voir les profilomètres des utilisateurs
        ('view_user_devices', 'Peut voir les profilomètres des utilisateurs'),
        ('configure_user_devices', 'Peut configurer les profilomètres des utilisateurs'),
        ('resolve_device_issues', 'Peut résoudre les problèmes des profilomètres'),
        
        # Gérer son stock
        ('manage_own_stock', 'Peut gérer son propre stock'),
        ('view_own_sales', 'Peut voir ses propres ventes'),
        ('create_device_models', 'Peut créer des modèles de profilomètres'),
        
        # Limiter l'accès aux données des autres vendeurs
        ('view_own_vendor_data', 'Peut voir uniquement ses propres données de vendeur'),
    ]
    
    # Créer les permissions
    for codename, name in vendor_permissions:
        Permission.objects.get_or_create(
            codename=codename,
            name=name,
            content_type=ContentType.objects.get_for_model(models.Model),
        )

class VendorPermissionsMixin:
    """Mixin pour ajouter des méthodes de vérification des permissions vendeur"""
    
    def can_view_user_device(self, user, device):
        """Vérifier si un vendeur peut voir un profilomètre d'utilisateur"""
        if user.has_perm('backapp.view_user_devices'):
            return True
        return False
    
    def can_configure_user_device(self, user, device):
        """Vérifier si un vendeur peut configurer un profilomètre d'utilisateur"""
        if user.has_perm('backapp.configure_user_devices'):
            return True
        return False
    
    def can_resolve_device_issues(self, user, device):
        """Vérifier si un vendeur peut résoudre les problèmes d'un profilomètre"""
        if user.has_perm('backapp.resolve_device_issues'):
            return True
        return False
    
    def can_manage_own_stock(self, user, vendor):
        """Vérifier si un utilisateur peut gérer le stock d'un vendeur spécifique"""
        if user.has_perm('backapp.manage_own_stock'):
            # Vérifier que l'utilisateur est bien le vendeur
            return hasattr(user, 'vendor_profile') and user.vendor_profile == vendor
        return False

# Permissions spécifiques pour l'administration
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

# Permissions pour les vendeurs (accès limité)
VENDOR_USER_PERMISSIONS = [
    'view_user_devices',
    'configure_user_devices',
    'resolve_device_issues',
    'manage_own_stock',
    'view_own_sales',
    'create_device_models',
    'view_own_vendor_data',
]

