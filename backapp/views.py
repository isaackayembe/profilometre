from rest_framework import status, generics, viewsets, permissions
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import default_token_generator
from allauth.account.models import EmailAddress
from allauth.account.utils import complete_signup
from allauth.account import app_settings as allauth_settings
from allauth.account.forms import LoginForm, SignupForm
from allauth.account.views import LoginView, SignupView
from allauth.account.adapter import get_adapter
from allauth.account.utils import perform_login, complete_signup
from allauth.account import signals
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import (
    UserSerializer, LoginSerializer, SignupSerializer,
    PasswordResetSerializer, PasswordResetConfirmSerializer,
    IoTSerializer, SensorDataSerializer, IoTDataInputSerializer,
    DataBatchSerializer, DataSessionSerializer, DeviceModelSerializer, StockSerializer, SaleSerializer, IoTSerializer
)
from .models import IoT, SensorData, DataBatch, DataSession, DeviceModel, Stock, Sale
from datetime import datetime
import uuid

@extend_schema(
    tags=['auth'],
    summary="Connexion utilisateur sécurisée",
    description="Endpoint pour connecter un utilisateur avec email et mot de passe (sécurisé avec allauth)",
    request=LoginSerializer,
    responses={
        200: UserSerializer,
        400: None,
    },
    examples=[
        OpenApiExample(
            'Connexion réussie',
            value={
                'token': 'your-auth-token-here',
                'user': {
                    'id': 1,
                    'email': 'user@example.com',
                    'first_name': 'John',
                    'last_name': 'Doe',
                    'date_joined': '2024-01-01T00:00:00Z'
                },
                'message': 'Connexion réussie'
            },
            response_only=True,
            status_codes=['200']
        ),
    ]
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """API endpoint pour la connexion sécurisée avec allauth"""
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        # Utiliser allauth pour l'authentification
        try:
            # Vérifier si l'email est vérifié
            email_address = EmailAddress.objects.get(email=email, primary=True)
            if not email_address.verified:
                return Response({
                    'error': 'Votre email n\'est pas vérifié. Veuillez vérifier votre email avant de vous connecter.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            user = email_address.user
        except EmailAddress.DoesNotExist:
            return Response({
                'error': 'Aucun utilisateur trouvé avec cet email.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Authentification avec allauth
        user = authenticate(username=user.username, password=password)
        if user is not None and user.is_active:
            # Utiliser allauth pour la connexion
            perform_login(request, user, allauth_settings.EMAIL_VERIFICATION)
            
            # Créer le token
            token, created = RefreshToken.for_user(user)
            
            return Response({
                'token': token.access_token,
                'user': UserSerializer(user).data,
                'message': 'Connexion réussie'
            })
        else:
            return Response({
                'error': 'Email ou mot de passe incorrect.'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    tags=['auth'],
    summary="Inscription utilisateur sécurisée",
    description="Endpoint pour créer un nouveau compte utilisateur (sécurisé avec allauth)",
    request=SignupSerializer,
    responses={
        201: UserSerializer,
        400: None,
    },
    examples=[
        OpenApiExample(
            'Inscription réussie',
            value={
                'token': 'your-auth-token-here',
                'user': {
                    'id': 1,
                    'email': 'newuser@example.com',
                    'first_name': 'Jane',
                    'last_name': 'Smith',
                    'date_joined': '2024-01-01T00:00:00Z'
                },
                'message': 'Inscription réussie. Vérifiez votre email pour confirmer votre compte.'
            },
            response_only=True,
            status_codes=['201']
        ),
    ]
)
@api_view(['POST'])
@permission_classes([AllowAny])
def signup_view(request):
    """API endpoint pour l'inscription sécurisée avec allauth"""
    serializer = SignupSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password1']
        first_name = serializer.validated_data.get('first_name', '')
        last_name = serializer.validated_data.get('last_name', '')
        
        # Vérifier si l'email existe déjà avec allauth
        if EmailAddress.objects.filter(email=email).exists():
            return Response({
                'error': 'Un utilisateur avec cet email existe déjà.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Créer l'utilisateur avec allauth
        username = email.split('@')[0]  # Utiliser la partie avant @ comme username
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        # Créer l'EmailAddress pour allauth
        email_address = EmailAddress.objects.create(
            user=user,
            email=email,
            primary=True,
            verified=False
        )
        
        # Utiliser allauth pour compléter l'inscription
        adapter = get_adapter(request)
        complete_signup(request, user, allauth_settings.EMAIL_VERIFICATION, None)
        
        # Envoyer le signal d'inscription
        signals.user_signed_up.send(
            sender=user.__class__,
            request=request,
            user=user
        )
        
        # Connecter l'utilisateur si l'email n'a pas besoin de vérification
        if allauth_settings.EMAIL_VERIFICATION != 'mandatory':
            perform_login(request, user, allauth_settings.EMAIL_VERIFICATION)
        
        # Créer le token
        token, created = RefreshToken.for_user(user)
        
        return Response({
            'token': token.access_token,
            'user': UserSerializer(user).data,
            'message': 'Inscription réussie. Vérifiez votre email pour confirmer votre compte.'
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    tags=['auth'],
    summary="Déconnexion utilisateur",
    description="Endpoint pour déconnecter un utilisateur",
    responses={
        200: None,
    }
)
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """API endpoint pour la déconnexion"""
    logout(request)
    return Response({'message': 'Déconnexion réussie'})

@extend_schema(
    tags=['users'],
    summary="Profil utilisateur",
    description="Récupérer les informations du profil utilisateur connecté",
    responses={
        200: UserSerializer,
    }
)
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """API endpoint pour récupérer le profil utilisateur"""
    return Response(UserSerializer(request.user).data)

@extend_schema(
    tags=['auth'],
    summary="Demande de réinitialisation de mot de passe",
    description="Demander un email de réinitialisation de mot de passe",
    request=PasswordResetSerializer,
    responses={
        200: None,
        400: None,
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_request(request):
    """API endpoint pour demander une réinitialisation de mot de passe"""
    serializer = PasswordResetSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
            # Ici vous pouvez implémenter l'envoi d'email
            # Pour l'instant, on retourne juste un message de succès
            return Response({
                'message': 'Si un compte existe avec cet email, vous recevrez un email de réinitialisation.'
            })
        except User.DoesNotExist:
            return Response({
                'message': 'Si un compte existe avec cet email, vous recevrez un email de réinitialisation.'
            })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    tags=['auth'],
    summary="Confirmation de réinitialisation de mot de passe",
    description="Confirmer la réinitialisation de mot de passe avec token",
    request=PasswordResetConfirmSerializer,
    responses={
        200: None,
        400: None,
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_confirm(request):
    """API endpoint pour confirmer la réinitialisation de mot de passe"""
    serializer = PasswordResetConfirmSerializer(data=request.data)
    if serializer.is_valid():
        try:
            uid = force_str(urlsafe_base64_decode(serializer.validated_data['uidb64']))
            user = User.objects.get(pk=uid)
            
            if default_token_generator.check_token(user, serializer.validated_data['token']):
                user.set_password(serializer.validated_data['new_password1'])
                user.save()
                return Response({'message': 'Mot de passe réinitialisé avec succès'})
            else:
                return Response({
                    'error': 'Le lien de réinitialisation est invalide ou a expiré.'
                }, status=status.HTTP_400_BAD_REQUEST)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({
                'error': 'Le lien de réinitialisation est invalide.'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    tags=['auth'],
    summary="Vérification d'email",
    description="Vérifier l'email d'un utilisateur avec la clé de confirmation",
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'key': {'type': 'string', 'description': 'Clé de confirmation d\'email'}
            },
            'required': ['key']
        }
    },
    responses={
        200: None,
        400: None,
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def email_verification(request):
    """API endpoint pour vérifier l'email avec allauth"""
    key = request.data.get('key')
    if not key:
        return Response({
            'error': 'Clé de confirmation requise.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        from allauth.account.models import EmailConfirmation
        confirmation = EmailConfirmation.objects.get(key=key)
        
        if confirmation.email_address.verified:
            return Response({
                'message': 'Email déjà vérifié.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Confirmer l'email
        confirmation.confirm(request)
        
        return Response({
            'message': 'Email vérifié avec succès. Vous pouvez maintenant vous connecter.'
        })
        
    except EmailConfirmation.DoesNotExist:
        return Response({
            'error': 'Clé de confirmation invalide ou expirée.'
        }, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    tags=['auth'],
    summary="Renvoyer la vérification d'email",
    description="Renvoyer l'email de vérification",
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'email': {'type': 'string', 'description': 'Email de l\'utilisateur'}
            },
            'required': ['email']
        }
    },
    responses={
        200: None,
        400: None,
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def resend_email_verification(request):
    """API endpoint pour renvoyer l'email de vérification"""
    email = request.data.get('email')
    if not email:
        return Response({
            'error': 'Email requis.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        email_address = EmailAddress.objects.get(email=email, primary=True)
        
        if email_address.verified:
            return Response({
                'message': 'Email déjà vérifié.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Renvoyer l'email de vérification
        adapter = get_adapter(request)
        adapter.send_confirmation_mail(request, email_address, signup=True)
        
        return Response({
            'message': 'Email de vérification renvoyé avec succès.'
        })
        
    except EmailAddress.DoesNotExist:
        return Response({
            'error': 'Aucun utilisateur trouvé avec cet email.'
        }, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    tags=['auth'],
    summary="Informations de session",
    description="Récupérer les informations de session de l'utilisateur connecté",
    responses={
        200: None,
        401: None,
    }
)
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def session_info(request):
    """API endpoint pour récupérer les informations de session"""
    user = request.user
    
    # Vérifier si l'email est vérifié
    try:
        email_address = EmailAddress.objects.get(user=user, primary=True)
        email_verified = email_address.verified
    except EmailAddress.DoesNotExist:
        email_verified = False
    
    return Response({
        'user_id': user.id,
        'email': user.email,
        'email_verified': email_verified,
        'is_active': user.is_active,
        'date_joined': user.date_joined,
        'last_login': user.last_login,
        'session_key': request.session.session_key,
    })

@extend_schema(
    tags=['auth'],
    summary="Changer le mot de passe",
    description="Changer le mot de passe de l'utilisateur connecté",
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'old_password': {'type': 'string', 'description': 'Ancien mot de passe'},
                'new_password1': {'type': 'string', 'description': 'Nouveau mot de passe'},
                'new_password2': {'type': 'string', 'description': 'Confirmation du nouveau mot de passe'}
            },
            'required': ['old_password', 'new_password1', 'new_password2']
        }
    },
    responses={
        200: None,
        400: None,
        401: None,
    }
)
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def change_password(request):
    """API endpoint pour changer le mot de passe"""
    old_password = request.data.get('old_password')
    new_password1 = request.data.get('new_password1')
    new_password2 = request.data.get('new_password2')
    
    if not all([old_password, new_password1, new_password2]):
        return Response({
            'error': 'Tous les champs sont requis.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if new_password1 != new_password2:
        return Response({
            'error': 'Les nouveaux mots de passe ne correspondent pas.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Vérifier l'ancien mot de passe
    if not request.user.check_password(old_password):
        return Response({
            'error': 'Ancien mot de passe incorrect.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Changer le mot de passe
    request.user.set_password(new_password1)
    request.user.save()
    
    # Déconnecter l'utilisateur pour qu'il se reconnecte
    logout(request)
    
    return Response({
        'message': 'Mot de passe changé avec succès. Veuillez vous reconnecter.'
    })

@extend_schema(
    tags=['iot'],
    summary="Envoi de données IoT avec session",
    description="API flexible pour recevoir les données de tous les capteurs IoT avec gestion de sessions par utilisateur",
    request=IoTDataInputSerializer,
    responses={
        201: SensorDataSerializer,
        400: None,
        401: None,
    },
    examples=[
        OpenApiExample(
            'Données de capteurs avec session',
            value={
                'device_id': 'RASPBERRY_PI_001',
                'session_id': 'session_2024_01_01_001',
                'sensor_readings': [
                    {
                        'sensor_type': 'temperature',
                        'value': 25.5,
                        'unit': '°C'
                    },
                    {
                        'sensor_type': 'humidity',
                        'value': 65.2,
                        'unit': '%'
                    },
                    {
                        'sensor_type': 'accelerometer',
                        'value': 9.81,
                        'unit': 'm/s²',
                        'additional_data': {
                            'x': 0.1,
                            'y': 0.2,
                            'z': 9.8
                        }
                    }
                ],
                'gps_latitude': 48.8566,
                'gps_longitude': 2.3522,
                'description': 'Session de test capteurs'
            },
            request_only=True,
            status_codes=['201']
        ),
    ]
)
@api_view(['POST'])
def send_iot_data_api_key(request):
    """
    Envoi de données IoT par l'équipement via clé API (X-API-KEY dans les headers)
    """
    api_key = request.headers.get('X-API-KEY')
    if not api_key:
        return Response({'error': 'Clé API manquante'}, status=401)
    try:
        device = IoT.objects.get(api_key=api_key)
    except IoT.DoesNotExist:
        return Response({'error': 'Clé API invalide'}, status=401)

    # On suppose que le body est identique à celui de send_iot_data
    data = request.data
    session_id = data.get('session_id')
    sensor_readings = data.get('sensor_readings', [])
    gps_lat = data.get('gps_latitude')
    gps_lon = data.get('gps_longitude')
    timestamp = data.get('timestamp')
    batch_id = data.get('batch_id')
    description = data.get('description', '')

    # Créer ou récupérer la session
    if session_id:
        session, session_created = DataSession.objects.get_or_create(
            session_id=session_id,
            device=device,
            defaults={
                'description': description,
                'is_active': True
            }
        )
    else:
        session = DataSession.objects.create(
            session_id=f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}",
            device=device,
            description=description,
            is_active=True
        )

    # Créer un lot de données si batch_id fourni
    data_batch = None
    if batch_id:
        data_batch, _ = DataBatch.objects.get_or_create(
            batch_id=batch_id,
            session=session,
            device=device,
            defaults={'data_count': 0}
        )

    # Traiter chaque lecture de capteur
    created_data = []
    for reading in sensor_readings:
        sensor_data = SensorData.objects.create(
            session=session,
            device=device,
            sensor_type=reading['sensor_type'],
            value=reading['value'],
            unit=reading.get('unit', ''),
            gps_latitude=gps_lat,
            gps_longitude=gps_lon,
            additional_data=reading.get('additional_data', {}),
            timestamp=timestamp if timestamp else datetime.now()
        )
        created_data.append(sensor_data)
        if data_batch:
            data_batch.data_count += 1
            data_batch.save()

    return Response({
        'message': f'{len(created_data)} lectures de capteurs enregistrées avec succès',
        'device': IoTSerializer(device).data,
        'session': DataSessionSerializer(session).data,
        'data_count': len(created_data),
        'batch_id': batch_id if data_batch else None
    }, status=201)
@extend_schema
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_front_data(request):
    """Récupérer les données des capteurs IoT de l'utilisateur connecté avec filtres"""
    try:
        # Récupérer les paramètres de filtrage
        device_id = request.GET.get('device_id')
        session_id = request.GET.get('session_id')
        sensor_type = request.GET.get('sensor_type')
        limit = request.GET.get('limit', 100)
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        # Construire la requête - FILTRER PAR UTILISATEUR CONNECTÉ
        queryset = SensorData.objects.filter(device__user=request.user)
        
        if device_id:
            queryset = queryset.filter(device__device_id=device_id)
        
        if session_id:
            queryset = queryset.filter(session__session_id=session_id)
        
        if sensor_type:
            queryset = queryset.filter(sensor_type=sensor_type)
        
        if start_date:
            queryset = queryset.filter(timestamp__date__gte=start_date)
        
        if end_date:
            queryset = queryset.filter(timestamp__date__lte=end_date)
        
        # Limiter les résultats
        try:
            limit = int(limit)
            queryset = queryset[:limit]
        except ValueError:
            queryset = queryset[:100]
        
        # Sérialiser les données
        serializer = SensorDataSerializer(queryset, many=True)
        
        return Response({
            'data': serializer.data,
            'count': len(serializer.data),
            'user': request.user.email,
            'filters_applied': {
                'device_id': device_id,
                'session_id': session_id,
                'sensor_type': sensor_type,
                'limit': limit,
                'start_date': start_date,
                'end_date': end_date
            }
        })
        
    except Exception as e:
        return Response({
            'error': f'Erreur lors de la récupération des données: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    tags=['iot'],
    summary="Récupération des sessions IoT",
    description="Récupérer toutes les sessions de collecte de données de l'utilisateur connecté",
    parameters=[
        OpenApiParameter(name='device_id', description='ID de l\'équipement', required=False, type=str),
        OpenApiParameter(name='is_active', description='Sessions actives uniquement', required=False, type=bool),
    ],
    responses={
        200: DataSessionSerializer,
        400: None,
    }
)
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_iot_sessions(request):
    """Récupérer les sessions de collecte de données de l'utilisateur connecté"""
    try:
        device_id = request.GET.get('device_id')
        is_active = request.GET.get('is_active')
        
        # Construire la requête - FILTRER PAR UTILISATEUR CONNECTÉ
        queryset = DataSession.objects.filter(device__user=request.user)
        
        if device_id:
            queryset = queryset.filter(device__device_id=device_id)
        
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        serializer = DataSessionSerializer(queryset, many=True)
        
        return Response({
            'sessions': serializer.data,
            'count': len(serializer.data),
            'user': request.user.email
        })
        
    except Exception as e:
        return Response({
            'error': f'Erreur lors de la récupération des sessions: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)

class IsVendeur(permissions.BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'vendeur_profile')
    def has_object_permission(self, request, view, obj):
        return obj.vendeur.user == request.user

class DeviceModelViewSet(viewsets.ModelViewSet):
    serializer_class = DeviceModelSerializer
    permission_classes = [permissions.IsAuthenticated, IsVendeur]
    def get_queryset(self):
        return DeviceModel.objects.filter(vendeur__user=self.request.user)
    def perform_create(self, serializer):
        serializer.save(vendeur=self.request.user.vendeur_profile)

class StockViewSet(viewsets.ModelViewSet):
    serializer_class = StockSerializer
    permission_classes = [permissions.IsAuthenticated, IsVendeur]
    def get_queryset(self):
        return Stock.objects.filter(vendeur__user=self.request.user)
    def perform_create(self, serializer):
        serializer.save(vendeur=self.request.user.vendeur_profile)

class SaleViewSet(viewsets.ModelViewSet):
    serializer_class = SaleSerializer
    permission_classes = [permissions.IsAuthenticated, IsVendeur]
    def get_queryset(self):
        return Sale.objects.filter(vendeur__user=self.request.user)
    def perform_create(self, serializer):
        serializer.save(vendeur=self.request.user.vendeur_profile)
