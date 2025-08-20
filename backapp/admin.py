from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import IoT, DataSession, SensorData, DataBatch, Vendeur , DeviceModel, Stock, Sale, DeviceConfiguration

# Register your models here.

@admin.register(Vendeur)
class VendeurAdmin(admin.ModelAdmin):
    """Administration des vendeurs de profilomètres"""
    list_display = ('company_name', 'user', 'vendor_id', 'is_verified', 'commission_rate', 'created_at')
    list_filter = ('is_verified', 'commission_rate', 'created_at')
    search_fields = ('company_name', 'vendor_id', 'user__username', 'user__email')
    list_editable = ('is_verified', 'commission_rate')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('user', 'company_name', 'vendor_id')
        }),
        ('Contact', {
            'fields': ('phone', 'address')
        }),
        ('Statut et commission', {
            'fields': ('is_verified', 'commission_rate')
        }),
        ('Horodatages', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

@admin.register(DeviceModel)
class DeviceModelAdmin(admin.ModelAdmin):
    """Administration des modèles de profilomètres"""
    list_display = ('name', 'model_number', 'vendeur', 'price', 'cost_price', 'is_active', 'created_at')
    list_filter = ('is_active', 'vendeur', 'created_at')
    search_fields = ('name', 'model_number', 'vendeur__company_name', 'description')
    list_editable = ('price', 'cost_price', 'is_active')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Informations du modèle', {
            'fields': ('vendeur', 'name', 'model_number', 'description')
        }),
        ('Prix et statut', {
            'fields': ('price', 'cost_price', 'is_active')
        }),
        ('Spécifications', {
            'fields': ('specifications',),
            'classes': ('collapse',)
        }),
        ('Horodatage', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('vendeur')

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    """Administration des stocks des vendeurs"""
    list_display = ('vendeur', 'device_model', 'quantity_available', 'quantity_reserved', 'total_quantity', 'reorder_level', 'last_updated')
    list_filter = ('vendeur', 'device_model', 'reorder_level', 'last_updated')
    search_fields = ('vendeur__company_name', 'device_model__name', 'device_model__model_number')
    list_editable = ('quantity_available', 'quantity_reserved', 'reorder_level')
    readonly_fields = ('last_updated',)
    
    fieldsets = (
        ('Stock', {
            'fields': ('vendeur', 'device_model')
        }),
        ('Quantités', {
            'fields': ('quantity_available', 'quantity_reserved', 'reorder_level')
        }),
        ('Localisation', {
            'fields': ('location',)
        }),
        ('Mise à jour', {
            'fields': ('last_updated',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('vendeur', 'device_model')

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    """Administration des ventes de profilomètres"""
    list_display = ('id', 'vendeur', 'customer', 'device_model', 'quantity', 'total_amount', 'commission_amount', 'status', 'sale_date')
    list_filter = ('status', 'sale_date', 'vendeur', 'device_model')
    search_fields = ('vendeur__company_name', 'customer__username', 'customer__email', 'device_model__name')
    list_editable = ('status',)
    readonly_fields = ('sale_date', 'total_amount', 'commission_amount')
    
    fieldsets = (
        ('Vente', {
            'fields': ('vendeur', 'customer', 'device_model', 'quantity')
        }),
        ('Prix et montants', {
            'fields': ('unit_price', 'total_amount', 'commission_amount')
        }),
        ('Statut et notes', {
            'fields': ('status', 'notes')
        }),
        ('Date', {
            'fields': ('sale_date',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('vendeur', 'customer', 'device_model')

@admin.register(DeviceConfiguration)
class DeviceConfigurationAdmin(admin.ModelAdmin):
    """Administration des configurations de profilomètres par les vendeurs"""
    list_display = ('device', 'vendeur', 'configuration_type', 'is_resolved', 'created_at', 'resolved_at')
    list_filter = ('configuration_type', 'is_resolved', 'vendeur', 'created_at')
    search_fields = ('device__name', 'device__device_id', 'vendeur__company_name', 'description')
    list_editable = ('is_resolved',)
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Configuration', {
            'fields': ('vendeur', 'device', 'configuration_type', 'description')
        }),
        ('Données de configuration', {
            'fields': ('configuration_data',),
            'classes': ('collapse',)
        }),
        ('Résolution', {
            'fields': ('is_resolved', 'resolution_notes', 'resolved_at')
        }),
        ('Horodatages', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('vendeur', 'device')

@admin.register(IoT)
class IoTDeviceAdmin(admin.ModelAdmin):
    """Administration des équipements IoT (profilomètres)"""
    list_display = ('name', 'device_id', 'user', 'vendeur', 'device_type', 'location', 'is_active', 'has_issues', 'created_at')
    list_filter = ('device_type', 'is_active', 'has_issues', 'vendeur', 'created_at', 'user')
    search_fields = ('name', 'device_id', 'user__username', 'user__email', 'location', 'vendeur__company_name')
    list_editable = ('is_active', 'has_issues', 'location')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('user', 'vendeur', 'name', 'device_id', 'device_type')
        }),
        ('Localisation et statut', {
            'fields': ('location', 'is_active')
        }),
        ('Problèmes', {
            'fields': ('has_issues', 'issue_description'),
            'classes': ('collapse',)
        }),
        ('Horodatages', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'vendeur')

@admin.register(DataSession)
class DataSessionAdmin(admin.ModelAdmin):
    """Administration des sessions de collecte de données"""
    list_display = ('session_id', 'device', 'start_time', 'end_time', 'is_active', 'data_count')
    list_filter = ('is_active', 'start_time', 'device__device_type', 'device__user')
    search_fields = ('session_id', 'device__name', 'device__user__username', 'description')
    list_editable = ('is_active',)
    readonly_fields = ('start_time',)  # 'created_at' supprimé car n'existe pas
    
    fieldsets = (
        ('Session', {
            'fields': ('session_id', 'device', 'description')
        }),
        ('Statut et horaires', {
            'fields': ('is_active', 'start_time', 'end_time')
        }),
    )
    
    def data_count(self, obj):
        """Afficher le nombre de données collectées dans cette session"""
        return obj.sensor_data.count()
    data_count.short_description = 'Données collectées'
    
    def get_queryset(self, request):
        """Optimiser les requêtes avec select_related et prefetch_related"""
        return super().get_queryset(request).select_related('device', 'device__user').prefetch_related('sensor_data')

@admin.register(SensorData)
class SensorDataAdmin(admin.ModelAdmin):
    """Administration des données des capteurs"""
    list_display = ('device', 'sensor_type', 'value', 'unit', 'timestamp', 'session', 'has_gps')
    list_filter = ('sensor_type', 'timestamp', 'device__device_type', 'device__user')
    search_fields = ('device__name', 'sensor_type', 'session__session_id', 'device__user__username')
    readonly_fields = ('timestamp',)  # 'created_at' supprimé car n'existe pas
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Données du capteur', {
            'fields': ('device', 'session', 'sensor_type', 'value', 'unit')
        }),
        ('Localisation GPS', {
            'fields': ('gps_latitude', 'gps_longitude'),
            'classes': ('collapse',)
        }),
        ('Données supplémentaires', {
            'fields': ('additional_data',),
            'classes': ('collapse',)
        }),
        ('Horodatage', {
            'fields': ('timestamp',),
            'classes': ('collapse',)
        }),
    )
    
    def has_gps(self, obj):
        """Indiquer si des coordonnées GPS sont disponibles"""
        return bool(obj.gps_latitude and obj.gps_longitude)
    has_gps.boolean = True
    has_gps.short_description = 'GPS'
    
    def get_queryset(self, request):
        """Optimiser les requêtes avec select_related"""
        return super().get_queryset(request).select_related('device', 'device__user', 'session')

@admin.register(DataBatch)
class DataBatchAdmin(admin.ModelAdmin):
    """Administration des lots de données"""
    list_display = ('batch_id', 'device', 'session', 'data_count', 'created_at')
    list_filter = ('created_at', 'device__device_type', 'device__user')
    search_fields = ('batch_id', 'device__name', 'session__session_id', 'device__user__username')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Informations du lot', {
            'fields': ('batch_id', 'device', 'session')
        }),
        ('Statistiques', {
            'fields': ('data_count', 'created_at')
        }),
    )
    
    def get_queryset(self, request):
        """Optimiser les requêtes avec select_related"""
        return super().get_queryset(request).select_related('device', 'device__user', 'session')

# Personnaliser l'interface d'administration des utilisateurs
class CustomUserAdmin(UserAdmin):
    """Administration personnalisée des utilisateurs avec leurs profilomètres"""
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'profilometre_count', 'last_login')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'groups', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    
    def profilometre_count(self, obj):
        """Afficher le nombre de profilomètres de l'utilisateur"""
        return obj.iot_devices.count()
    profilometre_count.short_description = 'Profilomètres'
    
    def get_queryset(self, request):
        """Optimiser les requêtes avec prefetch_related"""
        return super().get_queryset(request).prefetch_related('iot_devices')

# Désenregistrer et réenregistrer le modèle User avec notre admin personnalisé
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Configuration de l'interface d'administration
admin.site.site_header = "Administration Profilomètre"
admin.site.site_title = "Profilomètre Admin"
admin.site.index_title = "Gestion des Profilomètres et Utilisateurs"

# Configuration terminée - Interface d'administration prête pour les profilomètres
