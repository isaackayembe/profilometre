from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import ClientProfile
from .models import (
    ProfilometreLidarData, DeviceModel, DeviceInstance, Vente, VendeurProfile
)

User = get_user_model()

# -------------------------------
# Users
# -------------------------------
class UserSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'date_joined', 'status']

    def get_status(self, obj):
        if obj.is_superuser:
            return "super_user"
        elif obj.is_staff:
            return "administrateur"
        else:
            return "utilisateur"


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class SignupSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas")
        return data


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    new_password1 = serializers.CharField(write_only=True)
    new_password2 = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['new_password1'] != data['new_password2']:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas")
        return data


# -------------------------------
# Profilomètre Lidar
# -------------------------------
class ProfilometreLidarDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfilometreLidarData
        fields = [
            'id',
            'user_id',
            'session_id',
            'timestamp',
            'json_data',
            'has_lidar_data',
            'has_personality_data',
            'lidar_point_count',
            'lidar_capture_duration_sec',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'has_lidar_data',
            'has_personality_data',
            'lidar_point_count',
            'lidar_capture_duration_sec',
            'created_at',
            'updated_at',
        ]


# -------------------------------
# Device Models & Instances
# -------------------------------
class DeviceModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceModel
        fields = ['id', 'nom', 'prix', 'stock']
        read_only_fields = ['prix']  # Prix fixé par superuser


class DeviceInstanceSerializer(serializers.ModelSerializer):
    model = DeviceModelSerializer(read_only=True)
    model_id = serializers.PrimaryKeyRelatedField(queryset=DeviceModel.objects.all(), source='model', write_only=True)

    class Meta:
        model = DeviceInstance
        fields = ['id', 'serial', 'model', 'model_id', 'client', 'date_assigned']


# -------------------------------
# Ventes
# -------------------------------
class VenteSerializer(serializers.ModelSerializer):
    prix_unitaire = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    prix_total = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)

    class Meta:
        model = Vente
        fields = ['id', 'client', 'device_model', 'quantite', 'prix_unitaire', 'prix_total', 'date']

    def validate(self, data):
        device_model = data['device_model']
        quantite = data['quantite']
        if device_model.stock < quantite:
            raise serializers.ValidationError({'quantite': 'Stock insuffisant'})
        return data

    def create(self, validated_data):
        device_model = validated_data['device_model']
        quantite = validated_data['quantite']
        prix_unitaire = device_model.prix
        prix_total = prix_unitaire * quantite

        # Décrémenter le stock
        device_model.stock -= quantite
        device_model.save()

        vente = Vente.objects.create(
            vendeur=self.context['request'].user.vendeur_profile,
            client=validated_data.get('client'),
            device_model=device_model,
            quantite=quantite,
            prix_unitaire=prix_unitaire,
            prix_total=prix_total
        )
        return vente
#admin 

class UserAdminSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    role = serializers.ChoiceField(choices=['utilisateur','administrateur','superuser'], write_only=True, required=False)

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'date_joined', 'status', 'role']

    def get_status(self, obj):
        if obj.is_superuser:
            return "superuser"
        elif obj.is_staff:
            return "administrateur"
        else:
            return "utilisateur"

    def update(self, instance, validated_data):
        role = validated_data.pop('role', None)
        if role:
            if role == 'superuser':
                instance.is_superuser = True
                instance.is_staff = True
            elif role == 'administrateur':
                instance.is_superuser = False
                instance.is_staff = True
            else:  # utilisateur normal
                instance.is_superuser = False
                instance.is_staff = False
        return super().update(instance, validated_data)
    
class ClientProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientProfile
        fields = ['id', 'user', 'adresse', 'telephone', 'notes']
        depth = 1  # Pour inclure les infos du user (username, email, etc.)
    