from django.db import models
from django.contrib.auth.models import User

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