# Guide de Configuration pour les Équipes

## Pour l'équipe Frontend (React, Vue, Angular, WordPress)

### 1. Configuration CORS

L'API Django est configurée pour accepter les requêtes depuis les domaines de développement courants. Si vous utilisez un port différent, ajoutez-le dans `settings.py` :

```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React
    "http://localhost:8080",  # Vue.js
    "http://localhost:4200",  # Angular
    "http://localhost:8000",  # WordPress (si en local)
    # Ajoutez votre domaine ici
]
```

### 2. Utilisation avec WordPress

#### Option A: Plugin REST API
Installez un plugin comme "WP REST API" et utilisez les fonctions PHP suivantes :

```php
// Dans functions.php ou un plugin personnalisé
function profilometre_login($email, $password) {
    $api_url = 'http://localhost:8000/api/auth/login/';
    
    $response = wp_remote_post($api_url, array(
        'headers' => array(
            'Content-Type' => 'application/json',
        ),
        'body' => json_encode(array(
            'email' => $email,
            'password' => $password
        )),
        'timeout' => 30
    ));
    
    if (is_wp_error($response)) {
        return false;
    }
    
    $body = wp_remote_retrieve_body($response);
    $data = json_decode($body, true);
    
    if ($data && isset($data['token'])) {
        // Stocker le token dans la session WordPress
        $_SESSION['profilometre_token'] = $data['token'];
        $_SESSION['profilometre_user'] = $data['user'];
        return $data;
    }
    
    return false;
}

function profilometre_get_profile() {
    if (!isset($_SESSION['profilometre_token'])) {
        return false;
    }
    
    $api_url = 'http://localhost:8000/api/auth/profile/';
    
    $response = wp_remote_get($api_url, array(
        'headers' => array(
            'Authorization' => 'Token ' . $_SESSION['profilometre_token']
        ),
        'timeout' => 30
    ));
    
    if (is_wp_error($response)) {
        return false;
    }
    
    $body = wp_remote_retrieve_body($response);
    return json_decode($body, true);
}
```

#### Option B: JavaScript Frontend
Utilisez JavaScript pour communiquer avec l'API :

```javascript
// Dans votre thème WordPress ou plugin
class ProfilometreAPI {
    constructor(baseURL = 'http://localhost:8000') {
        this.baseURL = baseURL;
        this.token = localStorage.getItem('profilometre_token');
    }
    
    async login(email, password) {
        try {
            const response = await fetch(`${this.baseURL}/api/auth/login/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password })
            });
            
            const data = await response.json();
            if (response.ok) {
                this.token = data.token;
                localStorage.setItem('profilometre_token', data.token);
                return data;
            } else {
                throw new Error(data.error || 'Erreur de connexion');
            }
        } catch (error) {
            console.error('Erreur de connexion:', error);
            throw error;
        }
    }
    
    async getProfile() {
        if (!this.token) {
            throw new Error('Token non trouvé');
        }
        
        const response = await fetch(`${this.baseURL}/api/auth/profile/`, {
            headers: {
                'Authorization': `Token ${this.token}`
            }
        });
        
        return await response.json();
    }
    
    async logout() {
        if (!this.token) return;
        
        await fetch(`${this.baseURL}/api/auth/logout/`, {
            method: 'POST',
            headers: {
                'Authorization': `Token ${this.token}`
            }
        });
        
        this.token = null;
        localStorage.removeItem('profilometre_token');
    }
}

// Utilisation
const api = new ProfilometreAPI();

// Exemple de formulaire de connexion
document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    
    try {
        const result = await api.login(email, password);
        alert('Connexion réussie !');
        // Rediriger ou mettre à jour l'interface
    } catch (error) {
        alert('Erreur de connexion: ' + error.message);
    }
});
```

### 3. Utilisation avec React/Vue/Angular

#### React Example
```javascript
// hooks/useAuth.js
import { useState, useEffect } from 'react';

export const useAuth = () => {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(localStorage.getItem('token'));
    const [loading, setLoading] = useState(false);

    const login = async (email, password) => {
        setLoading(true);
        try {
            const response = await fetch('http://localhost:8000/api/auth/login/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });
            
            const data = await response.json();
            if (response.ok) {
                setToken(data.token);
                setUser(data.user);
                localStorage.setItem('token', data.token);
                return data;
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            throw error;
        } finally {
            setLoading(false);
        }
    };

    const logout = async () => {
        if (token) {
            await fetch('http://localhost:8000/api/auth/logout/', {
                method: 'POST',
                headers: { 'Authorization': `Token ${token}` }
            });
        }
        setToken(null);
        setUser(null);
        localStorage.removeItem('token');
    };

    return { user, token, login, logout, loading };
};
```

## Pour l'équipe Mobile (React Native, Flutter, etc.)

### React Native Example

```javascript
// services/authService.js
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_BASE_URL = 'http://localhost:8000';

export const authService = {
    async login(email, password) {
        try {
            const response = await fetch(`${API_BASE_URL}/api/auth/login/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password })
            });
            
            const data = await response.json();
            if (response.ok) {
                await AsyncStorage.setItem('token', data.token);
                await AsyncStorage.setItem('user', JSON.stringify(data.user));
                return data;
            } else {
                throw new Error(data.error || 'Erreur de connexion');
            }
        } catch (error) {
            console.error('Erreur de connexion:', error);
            throw error;
        }
    },

    async getProfile() {
        try {
            const token = await AsyncStorage.getItem('token');
            if (!token) throw new Error('Token non trouvé');

            const response = await fetch(`${API_BASE_URL}/api/auth/profile/`, {
                headers: {
                    'Authorization': `Token ${token}`
                }
            });
            
            return await response.json();
        } catch (error) {
            console.error('Erreur récupération profil:', error);
            throw error;
        }
    },

    async logout() {
        try {
            const token = await AsyncStorage.getItem('token');
            if (token) {
                await fetch(`${API_BASE_URL}/api/auth/logout/`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Token ${token}`
                    }
                });
            }
        } catch (error) {
            console.error('Erreur déconnexion:', error);
        } finally {
            await AsyncStorage.removeItem('token');
            await AsyncStorage.removeItem('user');
        }
    }
};
```

### Flutter Example

```dart
// services/auth_service.dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class AuthService {
  static const String baseUrl = 'http://localhost:8000';
  
  Future<Map<String, dynamic>> login(String email, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/auth/login/'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'email': email,
          'password': password,
        }),
      );
      
      final data = json.decode(response.body);
      if (response.statusCode == 200) {
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString('token', data['token']);
        await prefs.setString('user', json.encode(data['user']));
        return data;
      } else {
        throw Exception(data['error'] ?? 'Erreur de connexion');
      }
    } catch (e) {
      throw Exception('Erreur de connexion: $e');
    }
  }
  
  Future<Map<String, dynamic>> getProfile() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('token');
      if (token == null) throw Exception('Token non trouvé');
      
      final response = await http.get(
        Uri.parse('$baseUrl/api/auth/profile/'),
        headers: {'Authorization': 'Token $token'},
      );
      
      return json.decode(response.body);
    } catch (e) {
      throw Exception('Erreur récupération profil: $e');
    }
  }
  
  Future<void> logout() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('token');
      
      if (token != null) {
        await http.post(
          Uri.parse('$baseUrl/api/auth/logout/'),
          headers: {'Authorization': 'Token $token'},
        );
      }
    } catch (e) {
      print('Erreur déconnexion: $e');
    } finally {
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove('token');
      await prefs.remove('user');
    }
  }
}
```

## Configuration de Production

### 1. Variables d'environnement

Créez un fichier `.env` dans le répertoire racine :

```bash
# Django Settings
SECRET_KEY=votre-clé-secrète-très-sécurisée
DEBUG=False
ALLOWED_HOSTS=votre-domaine.com,www.votre-domaine.com

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=votre-mot-de-passe-app

# CORS Settings
CORS_ALLOWED_ORIGINS=https://votre-frontend.com,https://votre-wordpress.com

# Security Settings
CSRF_TRUSTED_ORIGINS=https://votre-frontend.com,https://votre-wordpress.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### 2. Déploiement

#### Avec Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python manage.py collectstatic --noinput

EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "profilometre.wsgi:application"]
```

#### Avec requirements.txt
```txt
Django==5.2
djangorestframework==3.16.0
django-allauth==0.60.1
django-cors-headers==4.3.1
drf-spectacular==0.28.0
gunicorn==21.2.0
python-decouple==3.8
```

## Tests

### Test des endpoints avec curl

```bash
# Test de connexion
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Test de récupération du profil (avec token)
curl -X GET http://localhost:8000/api/auth/profile/ \
  -H "Authorization: Token your-token-here"
```

### Test avec Postman

1. Importez la collection depuis l'URL Swagger : `http://localhost:8000/api/schema/`
2. Configurez les variables d'environnement pour l'URL de base
3. Testez les endpoints d'authentification

## Support et Maintenance

- **Documentation API** : http://localhost:8000/api/docs/
- **Logs** : Surveillez les logs Django pour les erreurs
- **Monitoring** : Configurez des alertes pour les erreurs 500
- **Backup** : Sauvegardez régulièrement la base de données

## Sécurité

- Changez la clé secrète Django en production
- Utilisez HTTPS en production
- Configurez des rate limits appropriés
- Surveillez les tentatives de connexion échouées
- Mettez à jour régulièrement les dépendances 