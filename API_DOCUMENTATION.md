# Documentation API Profilometre

## Vue d'ensemble

Cette API fournit des endpoints d'authentification sécurisés pour l'application Profilometre utilisant django-allauth et Django REST Framework.

## Base URL

```
http://localhost:8000
```

## Documentation Interactive

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **Schema OpenAPI**: http://localhost:8000/api/schema/

## Authentification

L'API utilise l'authentification par token. Après une connexion réussie, vous recevrez un token que vous devez inclure dans l'en-tête `Authorization` de vos requêtes.

```
Authorization: mon_boss your-token-here
```

## Endpoints

### 1. Connexion

**POST** `/api/auth/login/`

**Corps de la requête:**
```json
{
    "email": "user@example.com",
    "password": "votre_mot_de_passe"
}
```

**Réponse réussie (200):**
```json
{
    "token": "your-auth-token-here",
    "user": {
        "id": 1,
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "date_joined": "2024-01-01T00:00:00Z"
    },
    "message": "Connexion réussie"
}
```

### 2. Inscription

**POST** `/api/auth/signup/`

**Corps de la requête:**
```json
{
    "email": "newuser@example.com",
    "password1": "nouveau_mot_de_passe",
    "password2": "nouveau_mot_de_passe",
    "first_name": "Jane",
    "last_name": "Smith"
}
```

**Réponse réussie (201):**
```json
{
    "token": "your-auth-token-here",
    "user": {
        "id": 1,
        "email": "newuser@example.com",
        "first_name": "Jane",
        "last_name": "Smith",
        "date_joined": "2024-01-01T00:00:00Z"
    },
    "message": "Inscription réussie. Vérifiez votre email pour confirmer votre compte."
}
```

### 3. Déconnexion

**POST** `/api/auth/logout/`

**En-têtes requis:**
```
Authorization: mon_boss your-token-here
```

**Réponse réussie (200):**
```json
{
    "message": "Déconnexion réussie"
}
```

### 4. Profil utilisateur

**GET** `/api/auth/profile/`

**En-têtes requis:**
```
Authorization: mon_boss your-token-here
```

**Réponse réussie (200):**
```json
{
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "date_joined": "2024-01-01T00:00:00Z"
}
```

### 5. Demande de réinitialisation de mot de passe

**POST** `/api/auth/password-reset/`

**Corps de la requête:**
```json
{
    "email": "user@example.com"
}
```

**Réponse réussie (200):**
```json
{
    "message": "Si un compte existe avec cet email, vous recevrez un email de réinitialisation."
}
```

### 6. Confirmation de réinitialisation de mot de passe

**POST** `/api/auth/password-reset-confirm/`

**Corps de la requête:**
```json
{
    "new_password1": "nouveau_mot_de_passe",
    "new_password2": "nouveau_mot_de_passe",
    "token": "token_from_email",
    "uidb64": "uid_from_email"
}
```

**Réponse réussie (200):**
```json
{
    "message": "Mot de passe réinitialisé avec succès"
}
```

## Codes d'erreur

- **400 Bad Request**: Données invalides ou erreur de validation
- **401 Unauthorized**: Token manquant ou invalide
- **403 Forbidden**: Permissions insuffisantes
- **404 Not Found**: Ressource non trouvée
- **500 Internal Server Error**: Erreur serveur

## Exemples d'utilisation

### JavaScript (Fetch API)

```javascript
// Connexion
const login = async (email, password) => {
    const response = await fetch('http://localhost:8000/api/auth/login/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password })
    });
    
    const data = await response.json();
    if (response.ok) {
        localStorage.setItem('token', data.token);
        return data;
    } else {
        throw new Error(data.error || 'Erreur de connexion');
    }
};

// Récupérer le profil
const getProfile = async () => {
    const token = localStorage.getItem('token');
    const response = await fetch('http://localhost:8000/api/auth/profile/', {
        headers: {
            'Authorization': `mon_boss ${token}`
        }
    });
    
    return await response.json();
};
```

### React Native

```javascript
// Connexion
const login = async (email, password) => {
    try {
        const response = await fetch('http://localhost:8000/api/auth/login/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        if (response.ok) {
            // Stocker le token (AsyncStorage, SecureStore, etc.)
            await AsyncStorage.setItem('token', data.token);
            return data;
        } else {
            throw new Error(data.error || 'Erreur de connexion');
        }
    } catch (error) {
        console.error('Erreur:', error);
        throw error;
    }
};
```

### WordPress (PHP)

```php
// Connexion
function login_user($email, $password) {
    $url = 'http://localhost:8000/api/auth/login/';
    $data = array(
        'email' => $email,
        'password' => $password
    );
    
    $options = array(
        'http' => array(
            'header'  => "Content-type: application/json\r\n",
            'method'  => 'POST',
            'content' => json_encode($data)
        )
    );
    
    $context  = stream_context_create($options);
    $result = file_get_contents($url, false, $context);
    
    if ($result === FALSE) {
        return false;
    }
    
    return json_decode($result, true);
}

// Récupérer le profil
function get_user_profile($token) {
    $url = 'http://localhost:8000/api/auth/profile/';
    
    $options = array(
        'http' => array(
            'header'  => "Authorization: mon_boss $token\r\n",
            'method'  => 'GET'
        )
    );
    
    $context  = stream_context_create($options);
    $result = file_get_contents($url, false, $context);
    
    if ($result === FALSE) {
        return false;
    }
    
    return json_decode($result, true);
}
```

## Configuration CORS

L'API est configurée pour accepter les requêtes depuis les domaines suivants :
- `http://localhost:3000` (React)
- `http://127.0.0.1:3000`
- `http://localhost:8080` (Vue.js)
- `http://127.0.0.1:8080`
- `http://localhost:4200` (Angular)
- `http://127.0.0.1:4200`

Pour ajouter d'autres domaines, modifiez `CORS_ALLOWED_ORIGINS` dans `settings.py`.

## Sécurité

- Tous les mots de passe sont hachés avec bcrypt
- Les tokens d'authentification expirent à la déconnexion
- Protection CSRF activée
- Rate limiting configuré pour prévenir les attaques par force brute
- Validation stricte des emails
- Confirmation d'email obligatoire pour les nouveaux comptes

## Support

Pour toute question ou problème, consultez la documentation interactive ou contactez l'équipe de développement. 