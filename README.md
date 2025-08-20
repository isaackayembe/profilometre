# Profilometre - API d'Authentification Sécurisée

## 🚀 Vue d'ensemble

Profilometre est une API Django sécurisée utilisant django-allauth pour l'authentification et l'autorisation. Cette API peut être utilisée par des applications frontend (React, Vue, Angular, WordPress) et mobiles (React Native, Flutter).

## ✨ Fonctionnalités

- 🔐 Authentification sécurisée avec django-allauth
- 📧 Confirmation d'email obligatoire
- 🔑 Réinitialisation de mot de passe
- 🎫 Authentification par token
- 🌐 Support CORS pour les applications frontend
- 📚 Documentation API interactive (Swagger/OpenAPI)
- 🛡️ Protection contre les attaques par force brute
- 📱 Compatible mobile et web

## 🛠️ Technologies utilisées

- **Django 5.2** - Framework web Python
- **Django REST Framework** - API REST
- **django-allauth** - Authentification avancée
- **django-cors-headers** - Gestion CORS
- **drf-spectacular** - Documentation API
- **SQLite** - Base de données (développement)

## 📦 Installation

### Prérequis

- Python 3.8+
- pip

### Installation rapide

1. **Cloner le projet**
   ```bash
   git clone <votre-repo>
   cd profilometre
   ```

2. **Démarrer automatiquement**
   ```bash
   python start_server.py
   ```

### Installation manuelle

1. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

2. **Effectuer les migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Créer un superutilisateur**
   ```bash
   python manage.py createsuperuser
   ```

4. **Démarrer le serveur**
   ```bash
   python manage.py runserver
   ```

## 🌐 URLs importantes

- **Documentation API**: http://localhost:8000/api/docs/
- **Admin Django**: http://localhost:8000/admin/
- **API Auth**: http://localhost:8000/api/auth/

## 📚 Documentation

- [Documentation API complète](API_DOCUMENTATION.md)
- [Guide de configuration pour les équipes](TEAM_SETUP.md)

## 🔧 Configuration

### Variables d'environnement

Créez un fichier `.env` dans le répertoire racine :

```bash
# Django Settings
SECRET_KEY=votre-clé-secrète
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# CORS Settings
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080
```

### Configuration CORS

Pour ajouter de nouveaux domaines autorisés, modifiez `CORS_ALLOWED_ORIGINS` dans `settings.py` :

```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React
    "http://localhost:8080",  # Vue.js
    "http://localhost:4200",  # Angular
    "https://votre-domaine.com",  # Votre domaine
]
```

## 🔐 Endpoints d'authentification

### Connexion
```http
POST /api/auth/login/
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "password123"
}
```

### Inscription
```http
POST /api/auth/signup/
Content-Type: application/json

{
    "email": "newuser@example.com",
    "password1": "password123",
    "password2": "password123",
    "first_name": "John",
    "last_name": "Doe"
}
```

### Profil utilisateur
```http
GET /api/auth/profile/
Authorization: Token your-token-here
```

## 📱 Utilisation avec différentes plateformes

### WordPress
```php
$response = wp_remote_post('http://localhost:8000/api/auth/login/', [
    'headers' => ['Content-Type' => 'application/json'],
    'body' => json_encode([
        'email' => $email,
        'password' => $password
    ])
]);
```

### React
```javascript
const login = async (email, password) => {
    const response = await fetch('http://localhost:8000/api/auth/login/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
    });
    return await response.json();
};
```

### React Native
```javascript
const login = async (email, password) => {
    const response = await fetch('http://localhost:8000/api/auth/login/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
    });
    const data = await response.json();
    await AsyncStorage.setItem('token', data.token);
    return data;
};
```

## 🚀 Déploiement

### Production

1. **Configurer les variables d'environnement**
   ```bash
   DEBUG=False
   SECRET_KEY=votre-clé-secrète-sécurisée
   ALLOWED_HOSTS=votre-domaine.com
   ```

2. **Configurer l'email**
   ```bash
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=votre-email@gmail.com
   EMAIL_HOST_PASSWORD=votre-mot-de-passe-app
   ```

3. **Déployer avec Gunicorn**
   ```bash
   gunicorn --bind 0.0.0.0:8000 profilometre.wsgi:application
   ```

### Docker

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

## 🧪 Tests

### Test avec curl
```bash
# Connexion
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Profil (avec token)
curl -X GET http://localhost:8000/api/auth/profile/ \
  -H "Authorization: Token your-token-here"
```

### Test avec Postman
1. Importez la collection depuis : `http://localhost:8000/api/schema/`
2. Configurez l'URL de base : `http://localhost:8000`
3. Testez les endpoints d'authentification

## 🔒 Sécurité

- ✅ Mots de passe hachés avec bcrypt
- ✅ Protection CSRF
- ✅ Rate limiting
- ✅ Validation stricte des emails
- ✅ Tokens d'authentification sécurisés
- ✅ Confirmation d'email obligatoire

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🆘 Support

- 📖 [Documentation API](API_DOCUMENTATION.md)
- 📋 [Guide de configuration](TEAM_SETUP.md)
- 🐛 [Signaler un bug](https://github.com/votre-repo/issues)
- 💡 [Demander une fonctionnalité](https://github.com/votre-repo/issues)

## 📞 Contact

- **Email**: votre-email@example.com
- **GitHub**: [@votre-username](https://github.com/votre-username)

---

**Développé avec ❤️ pour sécuriser vos applications** 