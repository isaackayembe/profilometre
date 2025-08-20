from rest_framework.authentication import TokenAuthentication

class CustomTokenAuthentication(TokenAuthentication):
    """
    Cette classe permet d'utiliser l'authentification par token pour sécuriser les endpoints de l'API.
    Elle hérite de la classe DRF standard et peut être personnalisée (ex: changer le mot-clé d'en-tête).
    """
    keyword = 'Token'  # Par défaut, l'en-tête attendu est 'Authorization: Token <votre_token>'