from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json


class Vendeur(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='vendeur_profile')
    company_name = models.CharField(max_length=200)
    vendor_id = models.CharField(max_length=50, unique=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self): return self.company_name

class DeviceModel(models.Model):
    vendeur = models.ForeignKey(Vendeur, on_delete=models.CASCADE, related_name='device_models')
    name = models.CharField(max_length=100)
    model_number = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    specifications = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.name

class Stock(models.Model):
    vendeur = models.ForeignKey(Vendeur, on_delete=models.CASCADE, related_name='stock_items')
    device_model = models.ForeignKey(DeviceModel, on_delete=models.CASCADE, related_name='stock_items')
    quantity_available = models.IntegerField(default=0)
    quantity_reserved = models.IntegerField(default=0)
    reorder_level = models.IntegerField(default=5)
    location = models.CharField(max_length=200, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    @property
    def total_quantity(self):
        return self.quantity_available + self.quantity_reserved

    def __str__(self):
        return f"{self.device_model.name} - Stock: {self.quantity_available}"

class Sale(models.Model):
    SALE_STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('confirmed', 'Confirmée'),
        ('shipped', 'Expédiée'),
        ('delivered', 'Livrée'),
        ('cancelled', 'Annulée'),
    ]
    vendeur = models.ForeignKey(Vendeur, on_delete=models.CASCADE, related_name='sales')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchases')
    device_model = models.ForeignKey(DeviceModel, on_delete=models.CASCADE, related_name='sales')
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2)
    sale_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=SALE_STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    def __str__(self): return f"Vente #{self.id} - {self.device_model.name}"

class DeviceConfiguration(models.Model):
    vendeur = models.ForeignKey(Vendeur, on_delete=models.CASCADE, related_name='device_configurations')
    device = models.ForeignKey('IoT', on_delete=models.CASCADE, related_name='configurations')
    configuration_type = models.CharField(max_length=50)
    description = models.TextField()
    configuration_data = models.JSONField(default=dict, blank=True)
    is_resolved = models.BooleanField(default=False)
    resolution_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    def __str__(self): return f"Config {self.device.name} par {self.vendeur.company_name}"

class IoT(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='iot_devices')
    vendeur = models.ForeignKey(Vendeur, on_delete=models.CASCADE, related_name='sold_devices', null=True, blank=True)
    name = models.CharField(max_length=100)
    device_id = models.CharField(max_length=100, unique=True)
    device_type = models.CharField(max_length=50, default='Raspberry Pi')
    location = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    has_issues = models.BooleanField(default=False)
    issue_description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self): return f"{self.name} ({self.device_id})"

class DataSession(models.Model):
    device = models.ForeignKey(IoT, on_delete=models.CASCADE, related_name='data_sessions')
    session_id = models.CharField(max_length=100, unique=True)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    def __str__(self): return f"Session {self.session_id} - {self.device.name}"

class SensorData(models.Model):
    session = models.ForeignKey(DataSession, on_delete=models.CASCADE, related_name='sensor_data')
    device = models.ForeignKey(IoT, on_delete=models.CASCADE, related_name='sensor_data')
    sensor_type = models.CharField(max_length=50)
    value = models.FloatField()
    unit = models.CharField(max_length=20, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    gps_latitude = models.FloatField(null=True, blank=True)
    gps_longitude = models.FloatField(null=True, blank=True)
    additional_data = models.JSONField(default=dict, blank=True)
    def __str__(self): return f"{self.device.name} - {self.sensor_type}: {self.value}{self.unit}"

class DataBatch(models.Model):
    session = models.ForeignKey(DataSession, on_delete=models.CASCADE, related_name='data_batches')
    device = models.ForeignKey(IoT, on_delete=models.CASCADE, related_name='data_batches')
    batch_id = models.CharField(max_length=100, unique=True)
    data_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"Batch {self.batch_id} - {self.device.name}"
    
    
# models.py — version finale adaptée à votre format LiDAR (x,y,z)

class ProfilometreLidarData(models.Model):
    """
    Modèle unique pour stocker :
    - Données JSON du Profilomètre (psychométriques, comportementales)
    - Données LiDAR au format {x, y, z, timestamp_sec}
    - Tout dans un seul JSON, avec extraction intelligente
    """
    
    user_id = models.CharField(
        max_length=150,
        db_index=True,
        help_text="Identifiant unique de l'utilisateur ou du véhicule"
    )
    
    session_id = models.CharField(
        max_length=200,
        unique=True,
        help_text="Identifiant unique de la session (profilomètre + lidar)"
    )
    
    timestamp = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        help_text="Date et heure de la capture (session)"
    )
    
    # JSON principal : contient TOUT
    json_data = models.JSONField(
        help_text="Données complètes : profilomètre + lidar (format x,y,z) + metadata"
    )
    
    # Champs extraits pour requêtes rapides
    has_lidar_data = models.BooleanField(default=False, db_index=True)
    has_personality_data = models.BooleanField(default=False, db_index=True)
    lidar_point_count = models.IntegerField(default=0, db_index=True)
    lidar_capture_duration_sec = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Extraction intelligente
        profilometre_data = self.json_data.get('profile_data', {})
        lidar_points = self.json_data.get('lidar_data', [])
        
        # Détection de contenu
        self.has_personality_data = bool(profilometre_data.get('personality_traits'))
        self.has_lidar_data = isinstance(lidar_points, list) and len(lidar_points) > 0
        self.lidar_point_count = len(lidar_points) if self.has_lidar_data else 0
        
        # Calcul de la durée de capture (si timestamps disponibles)
        if self.has_lidar_data and len(lidar_points) >= 2:
            timestamps = [
                p.get('timestamp_sec') for p in lidar_points
                if p.get('timestamp_sec') is not None
            ]
            if len(timestamps) >= 2:
                self.lidar_capture_duration_sec = max(timestamps) - min(timestamps)
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Session {self.session_id} - User {self.user_id} @ {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        verbose_name = "Donnée Profilomètre + LiDAR (x,y,z)"
        verbose_name_plural = "Données Profilomètre + LiDAR (x,y,z)"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user_id', 'timestamp']),
            models.Index(fields=['has_lidar_data', 'lidar_point_count']),
        ]