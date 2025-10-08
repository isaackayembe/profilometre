from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json

# ---------------------------------------------------------
# 1️⃣ PROFILS D’UTILISATEURS : VENDEUR & CLIENT
# ---------------------------------------------------------

class VendeurProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='vendeur_profile')
    entreprise = models.CharField(max_length=100, blank=True, null=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    adresse = models.CharField(max_length=255, blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Vendeur : {self.user.username}"


class ClientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')
    vendeur = models.ForeignKey(VendeurProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='clients')
    espace_stockage = models.IntegerField(default=5)  # en Go
    distance_analyse = models.FloatField(default=50.0)  # en mètres
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Client : {self.user.username}"


# ---------------------------------------------------------
# 2️⃣ MODÈLES D’APPAREILS & INSTANCES PHYSIQUES
# ---------------------------------------------------------

class DeviceModel(models.Model):
    """Modèle d’appareil défini par le superuser"""
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    prix = models.DecimalField(max_digits=12, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    vendeur = models.ForeignKey(VendeurProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='device_models')

    def __str__(self):
        return f"{self.nom} - {self.prix} USD"


class DeviceInstance(models.Model):
    """Instance physique d’un appareil attribuée à un client"""
    serial = models.CharField(max_length=100, unique=True)
    model = models.ForeignKey(DeviceModel, on_delete=models.CASCADE, related_name='instances')
    client = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='devices')
    date_assigned = models.DateTimeField(blank=True, null=True)

    def assign_to(self, client):
        """Assigne l’appareil à un client"""
        self.client = client
        self.date_assigned = timezone.now()
        self.save()

    def __str__(self):
        return f"Appareil {self.serial} ({self.model.nom})"


# ---------------------------------------------------------
# 3️⃣ HISTORIQUE DES VENTES
# ---------------------------------------------------------

class Vente(models.Model):
    vendeur = models.ForeignKey(VendeurProfile, on_delete=models.CASCADE, related_name='ventes')
    client = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='achats')
    device_model = models.ForeignKey(DeviceModel, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField()
    prix_unitaire = models.DecimalField(max_digits=12, decimal_places=2)
    prix_total = models.DecimalField(max_digits=14, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Vente de {self.quantite} x {self.device_model.nom} par {self.vendeur.user.username}"
    
    
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
class Subscription(models.Model):
    """
    Modèle pour gérer les abonnements des utilisateurs
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    plan_name = models.CharField(max_length=100)  # Exemple : "Basic", "Pro"
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    max_devices = models.PositiveIntegerField(default=1)  # Nombre maximum d'appareils
    max_distance = models.FloatField(default=50.0)       # Distance maximale autorisée pour l'analyse (ex: km)

    def __str__(self):
        return f"{self.user.email} - {self.plan_name} ({'actif' if self.is_active else 'inactif'})"
    


class ClientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')
    adresse = models.CharField(max_length=255, blank=True, null=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Profil client de {self.user.username}"
