# 🔐 Guide d'utilisation de l'API Profilometre avec JWT

## Vue d'ensemble

L'API Profilometre utilise l'authentification JWT (JSON Web Tokens) pour sécuriser tous les endpoints. Chaque requête à l'API nécessite un token d'accès valide.

## 🔑 Endpoints d'authentification

### 1. Obtenir un token JWT

**POST** `/api/token/`

```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "votre_email@example.com",
    "password": "votre_mot_de_passe"
  }'
```

**Réponse :**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### 2. Rafraîchir un token

**POST** `/api/token/refresh/`

```bash
curl -X POST http://localhost:8000/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "votre_refresh_token"
  }'
```

### 3. Vérifier un token

**POST** `/api/token/verify/`

```bash
curl -X POST http://localhost:8000/api/token/verify/ \
  -H "Content-Type: application/json" \
  -d '{
    "token": "votre_access_token"
  }'
```

## 🛡️ Utilisation des tokens

### Headers requis

Pour tous les endpoints protégés, incluez le header d'autorisation :

```bash
Authorization: Bearer votre_access_token
```

### Exemple complet

```bash
# 1. Obtenir le token
TOKEN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "isaackayembe44@gmail.com",
    "password": "votre_mot_de_passe"
  }')

# 2. Extraire le token
ACCESS_TOKEN=$(echo $TOKEN_RESPONSE | jq -r '.access')

# 3. Utiliser le token pour accéder à l'API
curl -X GET http://localhost:8000/api/test-jwt/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json"
```

## 📡 Endpoints IoT protégés

### Envoyer des données IoT

**POST** `/api/iot/send-data/`

```bash
curl -X POST http://localhost:8000/api/iot/send-data/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "RASPBERRY_PI_001",
    "session_id": "session_2024_01_01_001",
    "sensor_readings": [
      {
        "sensor_type": "temperature",
        "value": 25.5,
        "unit": "°C"
      },
      {
        "sensor_type": "humidity",
        "value": 65.2,
        "unit": "%"
      }
    ],
    "gps_latitude": 48.8566,
    "gps_longitude": 2.3522,
    "description": "Données de test"
  }'
```

### Récupérer des données IoT

**GET** `/api/iot/get-data/`

```bash
curl -X GET "http://localhost:8000/api/iot/get-data/?limit=10&sensor_type=temperature" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

### Récupérer les sessions

**GET** `/api/iot/sessions/`

```bash
curl -X GET "http://localhost:8000/api/iot/sessions/?is_active=true" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

## 🔧 Configuration JWT

### Paramètres actuels

```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),  # 1 heure
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),     # 7 jours
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'AUTH_HEADER_TYPES': ('Bearer',),
}
```

## 🚨 Gestion des erreurs

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### Token expiré
```json
{
  "detail": "Token is invalid or expired"
}
```

## 🧪 Test de l'API

### Script de test automatique

Exécutez le script de test :

```bash
cd profilometre
python test_jwt_api.py
```

### Test manuel avec curl

```bash
# 1. Login
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"email": "isaackayembe44@gmail.com", "password": "votre_mot_de_passe"}'

# 2. Test endpoint protégé
curl -X GET http://localhost:8000/api/test-jwt/ \
  -H "Authorization: Bearer VOTRE_TOKEN_ICI"
```

## 🔒 Sécurité

### Bonnes pratiques

1. **Ne stockez jamais les tokens** dans le code source
2. **Utilisez HTTPS** en production
3. **Renouvelez les tokens** avant expiration
4. **Validez les tokens** côté client
5. **Logout** en invalidant le refresh token

### Logout

Pour se déconnecter, utilisez l'endpoint de logout :

```bash
curl -X POST http://localhost:8000/api/auth/logout/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

## 📚 Documentation complète

- **Swagger UI** : http://localhost:8000/api/docs/
- **ReDoc** : http://localhost:8000/api/redoc/
- **Schema OpenAPI** : http://localhost:8000/api/schema/

## 🚀 Démarrage rapide

1. **Démarrer le serveur** :
   ```bash
   python manage.py runserver
   ```

2. **Obtenir un token** :
   ```bash
   curl -X POST http://localhost:8000/api/token/ \
     -H "Content-Type: application/json" \
     -d '{"email": "isaackayembe44@gmail.com", "password": "votre_mot_de_passe"}'
   ```

3. **Tester l'API** :
   ```bash
   curl -X GET http://localhost:8000/api/test-jwt/ \
     -H "Authorization: Bearer VOTRE_TOKEN"
   ```

---

**Note** : Tous les endpoints IoT nécessitent un token JWT valide. Sans token, vous recevrez une erreur 401 Unauthorized. 