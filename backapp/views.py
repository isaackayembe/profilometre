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
from allauth.account.utils import setup_user_email
from django.contrib.auth.models import User
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
    ProfilometreLidarDataSerializer, DeviceModelSerializer, StockSerializer, SaleSerializer, IoTSerializer
)
from .models import IoT, SensorData, DataBatch, DataSession, DeviceModel, Stock, Sale
from datetime import datetime
import uuid
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from allauth.account.models import EmailAddress
from rest_framework_simplejwt.tokens import RefreshToken
from allauth.account.models import EmailAddress, EmailConfirmation
from .models import ProfilometreLidarData
from .serializers import ProfilometreLidarDataSerializer

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
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    email = serializer.validated_data['email']
    password = serializer.validated_data['password']

    # Récupérer l'utilisateur via allauth
    try:
        email_address = EmailAddress.objects.get(email=email, primary=True)
        user = email_address.user
    except EmailAddress.DoesNotExist:
        return Response({'error': 'Identifiants incorrects.'},
                        status=status.HTTP_401_UNAUTHORIZED)

    # Vérifier le mot de passe manuellement
    if not user.check_password(password) or not user.is_active:
        return Response({'error': 'Identifiants incorrects.'},
                        status=status.HTTP_401_UNAUTHORIZED)

    # Connexion via allauth
    perform_login(request, user, allauth_settings.EMAIL_VERIFICATION)

    # Générer le token JWT
    refresh = RefreshToken.for_user(user)
    return Response({
        'token': str(refresh.access_token),
        'refresh': str(refresh),
        'user': UserSerializer(user).data,
        'message': 'Connexion réussie'
    }, status=status.HTTP_200_OK)

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
@authentication_classes([])  # Pas d’auth requis
@permission_classes([AllowAny])
def signup_view(request):
    data = request.data
    email = data.get("email")
    password = data.get("password")
    username = data.get("username") or email
    first_name = data.get("first_name", "")
    last_name = data.get("last_name", "")

    if User.objects.filter(email=email).exists():
        return Response({"error": "Email déjà utilisé"}, status=status.HTTP_400_BAD_REQUEST)

    # Si tu veux activer directement, mets is_active=True
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        is_active=True  # L'utilisateur est actif tout de suite
    )

    # Générer le token JWT
    refresh = RefreshToken.for_user(user)

    return Response({
        "success": True,
        "message": "Inscription réussie. Vous êtes connecté.",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
        },
        "tokens": {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }
    }, status=status.HTTP_201_CREATED)


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
        
        # ✅ Créer une confirmation
        confirmation = EmailConfirmation.create(email_address)
        confirmation.send(request)

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

@api_view(['POST'])
@permission_classes([AllowAny])  # Mets IsAuthenticated si tu veux protéger
def send_profilometre_lidar_data(request):
    """
    POST : Crée une nouvelle session Profilomètre+LiDAR
    """
    serializer = ProfilometreLidarDataSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

@api_view(['GET'])
@permission_classes([AllowAny])  # Mets IsAuthenticated si tu veux protéger
def list_profilometre_lidar_data(request):
    """
    GET : Liste toutes les sessions Profilomètre+LiDAR
    """
    queryset = ProfilometreLidarData.objects.all().order_by('-timestamp')
    user_id = request.GET.get('user_id')
    if user_id:
        queryset = queryset.filter(user_id=user_id)
    serializer = ProfilometreLidarDataSerializer(queryset, many=True)
    return Response(serializer.data)


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
