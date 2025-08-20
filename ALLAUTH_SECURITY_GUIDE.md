# 🔐 Guide de Sécurité Allauth - Profilometre

## 🎯 Vue d'ensemble

Votre application Profilometre utilise maintenant **django-allauth** pour une authentification sécurisée. Voici les améliorations apportées :

## 🛡️ Améliorations de Sécurité

### 1. **Vérification d'Email Obligatoire**
- ✅ Tous les nouveaux utilisateurs doivent vérifier leur email
- ✅ Impossible de se connecter sans email vérifié
- ✅ Protection contre les comptes fictifs

### 2. **Gestion Sécurisée des Sessions**
- ✅ Utilisation des fonctions allauth pour la connexion
- ✅ Sessions sécurisées avec expiration
- ✅ Protection contre les attaques de session

### 3. **Rate Limiting Intégré**
```python
ACCOUNT_RATE_LIMITS = {
    'login_failed': '5/m',      # 5 tentatives par minute
    'signup': '10/h',           # 10 inscriptions par heure
    'password_reset': '5/h',    # 5 réinitialisations par heure
    'email_confirmation': '10/h' # 10 confirmations par heure
}
```

### 4. **Validation Stricte des Emails**
- ✅ Vérification de l'unicité des emails
- ✅ Validation du format email
- ✅ Protection contre l'énumération d'emails

## 🔗 Nouveaux Endpoints Sécurisés

### **Authentification de Base**
```
POST /api/auth/login/          # Connexion avec vérification email
POST /api/auth/signup/         # Inscription avec allauth
POST /api/auth/logout/         # Déconnexion sécurisée
GET  /api/auth/profile/        # Profil utilisateur
```

### **Gestion des Emails**
```
POST /api/auth/email-verify/   # Vérifier email avec clé
POST /api/auth/email-resend/   # Renvoyer email de vérification
```

### **Sécurité Avancée**
```
GET  /api/auth/session-info/   # Informations de session
POST /api/auth/change-password/ # Changer mot de passe
```

## 🚀 Utilisation des APIs

### **1. Inscription Sécurisée**
```bash
curl -X POST http://localhost:8000/api/auth/signup/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password1": "securepassword123",
    "password2": "securepassword123",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

**Réponse :**
```json
{
  "token": "your-auth-token",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe"
  },
  "message": "Inscription réussie. Vérifiez votre email pour confirmer votre compte."
}
```

### **2. Connexion avec Vérification Email**
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

**Si email non vérifié :**
```json
{
  "error": "Votre email n'est pas vérifié. Veuillez vérifier votre email avant de vous connecter."
}
```

### **3. Vérification d'Email**
```bash
curl -X POST http://localhost:8000/api/auth/email-verify/ \
  -H "Content-Type: application/json" \
  -d '{
    "key": "email-confirmation-key-from-email"
  }'
```

### **4. Informations de Session**
```bash
curl -X GET http://localhost:8000/api/auth/session-info/ \
  -H "Authorization: Token your-auth-token"
```

**Réponse :**
```json
{
  "user_id": 1,
  "email": "user@example.com",
  "email_verified": true,
  "is_active": true,
  "date_joined": "2024-01-01T00:00:00Z",
  "last_login": "2024-01-01T12:00:00Z",
  "session_key": "session-key"
}
```

## 🔧 Configuration Allauth

### **Settings.py - Configuration Sécurité**
```python
# Allauth settings
ACCOUNT_AUTHENTICATION_METHOD = 'email'  # Authentification par email
ACCOUNT_EMAIL_REQUIRED = True            # Email obligatoire
ACCOUNT_EMAIL_VERIFICATION = 'mandatory' # Vérification email obligatoire
ACCOUNT_USERNAME_REQUIRED = False        # Username optionnel
ACCOUNT_UNIQUE_EMAIL = True              # Email unique
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3  # Expiration en 3 jours

# Rate limiting
ACCOUNT_RATE_LIMITS = {
    'login_failed': '5/m',
    'signup': '10/h',
    'password_reset': '5/h',
    'email_confirmation': '10/h',
}
```

## 🛡️ Fonctionnalités de Sécurité

### **1. Protection contre les Attaques par Force Brute**
- Limitation à 5 tentatives de connexion par minute
- Blocage temporaire après échecs répétés

### **2. Protection contre l'Énumération d'Emails**
- Messages d'erreur génériques
- Impossible de deviner si un email existe

### **3. Sessions Sécurisées**
- Tokens d'authentification uniques
- Expiration automatique des sessions
- Déconnexion sécurisée

### **4. Validation des Mots de Passe**
- Validation Django standard
- Hachage sécurisé avec bcrypt
- Protection contre les mots de passe faibles

## 📧 Configuration Email

### **Développement (Console)**
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

### **Production (SMTP)**
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

## 🧪 Tests de Sécurité

### **Test de Connexion avec Email Non Vérifié**
```bash
# 1. Créer un compte
curl -X POST http://localhost:8000/api/auth/signup/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password1": "password123", "password2": "password123"}'

# 2. Essayer de se connecter (doit échouer)
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

### **Test de Rate Limiting**
```bash
# Essayer plusieurs connexions échouées rapidement
for i in {1..6}; do
  curl -X POST http://localhost:8000/api/auth/login/ \
    -H "Content-Type: application/json" \
    -d '{"email": "wrong@example.com", "password": "wrongpassword"}'
done
```

## 🔍 Monitoring et Logs

### **Logs de Sécurité à Surveiller**
- Tentatives de connexion échouées
- Tentatives d'inscription
- Demandes de réinitialisation de mot de passe
- Vérifications d'email

### **Métriques Importantes**
- Taux de succès des connexions
- Nombre de comptes créés
- Emails de vérification envoyés
- Tentatives de force brute

## 🚨 Bonnes Pratiques

### **1. En Production**
- ✅ Utiliser HTTPS
- ✅ Configurer un backend email SMTP
- ✅ Surveiller les logs de sécurité
- ✅ Mettre à jour régulièrement les dépendances

### **2. Gestion des Erreurs**
- ✅ Messages d'erreur génériques
- ✅ Logs détaillés côté serveur
- ✅ Pas d'informations sensibles dans les réponses

### **3. Tokens d'Authentification**
- ✅ Stockage sécurisé côté client
- ✅ Expiration automatique
- ✅ Régénération après changement de mot de passe

## 📚 Ressources

- [Documentation django-allauth](https://django-allauth.readthedocs.io/)
- [Guide de sécurité Django](https://docs.djangoproject.com/en/5.2/topics/security/)
- [Documentation API Profilometre](API_DOCUMENTATION.md)

---

**🔐 Votre application est maintenant sécurisée avec les meilleures pratiques d'authentification !** 