from rest_framework import status, viewsets, permissions
from rest_framework.decorators import api_view, permission_classes, authentication_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import get_user_model, logout
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import default_token_generator
from allauth.account.utils import perform_login
from allauth.account.models import EmailAddress, EmailConfirmation
from drf_spectacular.utils import extend_schema, OpenApiExample

from .serializers import (
    UserSerializer, LoginSerializer, SignupSerializer,
    PasswordResetSerializer, PasswordResetConfirmSerializer,
    ProfilometreLidarDataSerializer, DeviceModelSerializer,
    DeviceInstanceSerializer, VenteSerializer, UserAdminSerializer
)
from .models import DeviceModel, DeviceInstance, Vente, ProfilometreLidarData, Subscription, ClientProfile
from .permissions import IsSuperUser, IsVendeur
from .serializers import ClientProfileSerializer
from .permissions import IsVendeur, IsSuperUser

User = get_user_model()

# -------------------- AUTH --------------------
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    email = serializer.validated_data['email']
    password = serializer.validated_data['password']

    try:
        email_address = EmailAddress.objects.get(email=email, primary=True)
        user = email_address.user
    except EmailAddress.DoesNotExist:
        return Response({'error': 'Identifiants incorrects.'}, status=status.HTTP_401_UNAUTHORIZED)

    if not user.check_password(password) or not user.is_active:
        return Response({'error': 'Identifiants incorrects.'}, status=status.HTTP_401_UNAUTHORIZED)

    perform_login(request, user, True)
    refresh = RefreshToken.for_user(user)
    user_status = "utilisateur"
    if user.is_superuser:
        user_status = "super_user"
    elif user.is_staff:
        user_status = "administrateur"

    return Response({
        'token': str(refresh.access_token),
        'refresh': str(refresh),
        'user': UserSerializer(user).data,
        'status': user_status,
        'message': 'Connexion réussie'
    }, status=status.HTTP_200_OK)
    
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def change_password(request):
    user = request.user
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')

    if not old_password or not new_password:
        return Response({'error': 'Ancien et nouveau mot de passe requis'}, status=400)

    if not user.check_password(old_password):
        return Response({'error': 'Ancien mot de passe incorrect'}, status=400)

    user.set_password(new_password)
    user.save()
    return Response({'message': 'Mot de passe changé avec succès'})


@api_view(['POST'])
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

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        is_active=True
    )

    refresh = RefreshToken.for_user(user)
    return Response({
        "success": True,
        "message": "Inscription réussie. Vous êtes connecté.",
        "user": UserSerializer(user).data,
        "tokens": {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }
    }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def logout_view(request):
    logout(request)
    return Response({'message': 'Déconnexion réussie'})

# -------------------- USER PROFILE --------------------
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])

def user_profile(request):
    """API endpoint pour récupérer le profil utilisateur"""
    return Response(UserSerializer(request.user).data)

# -------------------- PASSWORD --------------------
@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_request(request):
    serializer = PasswordResetSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        return Response({'message': 'Si un compte existe avec cet email, vous recevrez un email.'})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_confirm(request):
    serializer = PasswordResetConfirmSerializer(data=request.data)
    if serializer.is_valid():
        try:
            uid = force_str(urlsafe_base64_decode(serializer.validated_data['uidb64']))
            user = User.objects.get(pk=uid)
            
            if default_token_generator.check_token(user, serializer.validated_data['token']):
                user.set_password(serializer.validated_data['new_password1'])
                user.save()
                return Response({'message': 'Mot de passe réinitialisé avec succès'})
        except:
            return Response({'error': 'Lien invalide.'}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# -------------------- LIDAR / MOBILE --------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_profilometre_lidar_data(request):
    user_id = request.data.get('user_id')
    distance = request.data.get('distance')

    try:
        subscription = Subscription.objects.get(user__id=user_id)
        if not subscription.is_active() or subscription.space_consumed >= subscription.total_space or distance > subscription.distance_limit:
            return Response({"error": "Limite dépassée."}, status=403)

        serializer = ProfilometreLidarDataSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
    except Subscription.DoesNotExist:
        return Response({"error": "Aucun abonnement trouvé."}, status=404)

    return Response({"error": "Données invalides."}, status=400)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_user_details(request):
    user = request.user
    try:
        subscription = Subscription.objects.get(user=user)
        analyses = ProfilometreLidarData.objects.filter(user=user)
        total_distance = sum(a.distance for a in analyses)
        user_info = {
            "user_id": user.id,
            "analyses": ProfilometreLidarDataSerializer(analyses, many=True).data,
            "subscription": {
                "total_space": subscription.total_space,
                "space_consumed": subscription.space_consumed,
                "distance_limit": subscription.distance_limit,
                "expiration_date": subscription.expiration_date,
            }
        }
        return Response(user_info)
    except Subscription.DoesNotExist:
        return Response({"error": "Aucun abonnement trouvé."}, status=404)

# -------------------- VENDEUR --------------------
class DeviceInstanceViewSet(viewsets.ModelViewSet):
    serializer_class = DeviceInstanceSerializer
    permission_classes = [IsAuthenticated, IsVendeur]

    def get_queryset(self):
        return DeviceInstance.objects.filter(model__vendeur=self.request.user.vendeur_profile)

    @action(detail=True, methods=['post'])
    def assign_client(self, request, pk=None):
        instance = self.get_object()
        email = request.data.get('email')
        if not email:
            return Response({'detail': 'Email requis'}, status=400)
        try:
            client = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'detail': 'Client non trouvé'}, status=404)
        instance.assign_to(client)
        return Response({'status': 'assigné'})

class VenteViewSet(viewsets.ModelViewSet):
    serializer_class = VenteSerializer
    permission_classes = [IsAuthenticated, IsVendeur]

    def get_queryset(self):
        return Vente.objects.filter(vendeur__user=self.request.user).order_by('-date')

# -------------------- ADMIN --------------------
class UserAdminViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserAdminSerializer
    permission_classes = [IsAuthenticated, IsSuperUser]
    authentication_classes = [JWTAuthentication]
    http_method_names = ['get', 'put', 'patch', 'delete', 'head', 'options']

class DeviceModelViewSet(viewsets.ModelViewSet):
    """
    API pour les modèles d'appareil gérés par le vendeur.
    """
    serializer_class = DeviceModelSerializer
    permission_classes = [permissions.IsAuthenticated, IsVendeur]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        # Limiter aux modèles appartenant au vendeur connecté
        return DeviceModel.objects.filter(vendeur=self.request.user.vendeur_profile)

    def perform_create(self, serializer):
        # Associer le modèle au vendeur connecté
        serializer.save(vendeur=self.request.user.vendeur_profile)
        
        
        
class ClientViewSet(viewsets.ModelViewSet):
            
    """
    API pour gérer les clients d'un vendeur.
    """
    serializer_class = ClientProfileSerializer
    permission_classes = [IsAuthenticated, IsVendeur]

    def get_queryset(self):
        # Récupère uniquement les clients liés au vendeur connecté
        return ClientProfile.objects.filter(vendeur=self.request.user.vendeur_profile)

    @action(detail=False, methods=['post'])
    def update_by_email(self, request):
        """
        Mettre à jour un client par email.
        """
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email requis'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            client_profile = user.client_profile
            # Exemple: mettre à jour un champ du client, ici "notes"
            client_profile.notes = request.data.get('notes', client_profile.notes)
            client_profile.save()
            return Response({'message': 'Client mis à jour avec succès'})
        except User.DoesNotExist:
            return Response({'error': 'Client non trouvé'}, status=status.HTTP_404_NOT_FOUND)
