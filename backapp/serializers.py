from rest_framework import serializers
from django.contrib.auth.models import User
from .models import IoT, ProfilometreLidarData, SensorData, DataBatch, DataSession, DeviceModel, Stock, Sale

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'date_joined']

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class SignupSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PasswordResetConfirmSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    new_password1 = serializers.CharField(write_only=True)
    new_password2 = serializers.CharField(write_only=True)

# IoT Serializers
class IoTSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    api_key = serializers.CharField(read_only=True)  # <-- Ajoute cette ligne

    class Meta:
        model = IoT
        fields = [
            'id', 'user', 'user_email', 'name', 'device_id', 'device_type',
            'location', 'is_active', 'created_at', 'updated_at', 'api_key'  # <-- Ajoute 'api_key'
        ]
        read_only_fields = ['user', 'user_email', 'created_at', 'updated_at', 'api_key']

class DataSessionSerializer(serializers.ModelSerializer):
    device_name = serializers.CharField(source='device.name', read_only=True)
    device_id = serializers.CharField(source='device.device_id', read_only=True)
    
    class Meta:
        model = DataSession
        fields = ['id', 'session_id', 'device', 'device_name', 'device_id', 'start_time', 'end_time', 'is_active', 'description']

class SensorDataSerializer(serializers.ModelSerializer):
    device_name = serializers.CharField(source='device.name', read_only=True)
    session_id = serializers.CharField(source='session.session_id', read_only=True)
    
    class Meta:
        model = SensorData
        fields = ['id', 'session', 'session_id', 'device', 'device_name', 'sensor_type', 'value', 'unit', 'timestamp', 
                 'gps_latitude', 'gps_longitude', 'additional_data']


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

class SensorReadingSerializer(serializers.Serializer):
    """Sérialiseur pour une lecture de capteur individuelle"""
    sensor_type = serializers.CharField(help_text="Type de capteur (temperature, humidity, accelerometer, etc.)")
    value = serializers.FloatField(help_text="Valeur mesurée")
    unit = serializers.CharField(required=False, help_text="Unité de mesure")
    additional_data = serializers.DictField(required=False, help_text="Données supplémentaires")

class DataBatchSerializer(serializers.ModelSerializer):
    sensor_data = SensorDataSerializer(many=True, read_only=True)
    session_id = serializers.CharField(source='session.session_id', read_only=True)
    
    class Meta:
        model = DataBatch
        fields = ['id', 'batch_id', 'session', 'session_id', 'device', 'data_count', 'created_at', 'sensor_data']

class DeviceModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceModel
        fields = '__all__'
        read_only_fields = ['vendeur']

class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = '__all__'
        read_only_fields = ['vendeur']

class SaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sale
        fields = '__all__'
        read_only_fields = ['vendeur']