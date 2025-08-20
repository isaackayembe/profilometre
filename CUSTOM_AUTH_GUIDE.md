# Guide de Personnalisation de l'En-tête d'Authentification

## 🔧 Comment changer le préfixe d'authentification

Vous pouvez facilement changer le préfixe d'authentification de "mon_boss" vers n'importe quoi d'autre.

### **Option 1: Changer rapidement dans `authentication.py`**

Modifiez la ligne 8 dans `backapp/authentication.py` :

```python
class CustomTokenAuthentication(TokenAuthentication):
    # Changez cette ligne pour votre préfixe préféré
    keyword = 'mon_boss'  # ← Changez ici !
```

**Exemples de préfixes populaires :**

```python
# Standard JWT
keyword = 'Bearer'

# API Key style
keyword = 'API-Key'

# Custom style
keyword = 'Custom'

# Simple style
keyword = 'Auth'

# Votre propre style
keyword = 'Profilometre-Auth'
keyword = 'MyApp-Token'
keyword = 'Secure-Key'
keyword = 'mon_boss'  # Préfixe actuel
```

### **Option 2: Utiliser une classe prête à l'emploi**

Nous avons créé plusieurs classes prêtes à l'emploi dans `authentication.py` :

```python
# Pour utiliser "API-Key"
from backapp.authentication import APIKeyAuthentication

# Pour utiliser "Custom"
from backapp.authentication import CustomAuthAuthentication

# Pour utiliser "Auth"
from backapp.authentication import AuthHeaderAuthentication
```

Puis modifiez `settings.py` :

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'backapp.authentication.APIKeyAuthentication',  # ← Changez ici !
        'rest_framework.authentication.SessionAuthentication',
    ],
    # ...
}
```

### **Option 3: Créer votre propre classe**

Créez une nouvelle classe dans `authentication.py` :

```python
class MyCustomAuthentication(TokenAuthentication):
    """
    Authentification avec votre préfixe personnalisé
    """
    keyword = 'Mon-Prefixe-Personnalise'
```

## 📝 Exemples d'utilisation

### **Avec "mon_boss" (actuel)**
```javascript
headers: {
    'Authorization': 'mon_boss your-token-here'
}
```

### **Avec "API-Key"**
```javascript
headers: {
    'Authorization': 'API-Key your-token-here'
}
```

### **Avec "Custom"**
```javascript
headers: {
    'Authorization': 'Custom your-token-here'
}
```

### **Avec "Auth"**
```javascript
headers: {
    'Authorization': 'Auth your-token-here'
}
```

### **Avec votre préfixe personnalisé**
```javascript
headers: {
    'Authorization': 'Mon-Prefixe-Personnalise your-token-here'
}
```

## 🔄 Mise à jour de la documentation

Après avoir changé le préfixe, mettez à jour :

1. **`API_DOCUMENTATION.md`** - Tous les exemples d'en-têtes
2. **`TEAM_SETUP.md`** - Les exemples de code
3. **`test_api.py`** - Les tests
4. **Vos applications frontend/mobile**

## 🧪 Test du changement

Après avoir changé le préfixe, testez avec :

```bash
python test_api.py
```

Ou avec curl :

```bash
# Ancien format (ne fonctionnera plus)
curl -H "Authorization: Token your-token" http://localhost:8000/api/auth/profile/

# Nouveau format
curl -H "Authorization: mon_boss your-token" http://localhost:8000/api/auth/profile/
```

## 📋 Préfixes recommandés

| Préfixe | Usage | Standard |
|---------|-------|----------|
| `Bearer` | JWT/Token standard | ✅ OAuth 2.0 |
| `API-Key` | Clés API | ✅ Common |
| `Token` | Tokens simples | ✅ DRF default |
| `Auth` | Authentification simple | ✅ Custom |
| `Custom` | Votre propre style | ✅ Custom |

## ⚠️ Important

- **Cohérence** : Utilisez le même préfixe partout dans votre application
- **Documentation** : Mettez à jour tous vos exemples de code
- **Tests** : Vérifiez que tous vos tests utilisent le bon préfixe
- **Équipes** : Informez vos équipes frontend/mobile du changement

## 🚀 Exemple complet de changement

1. **Changer le préfixe** dans `authentication.py` :
   ```python
   keyword = 'API-Key'  # Au lieu de 'Bearer'
   ```

2. **Mettre à jour la documentation** :
   ```markdown
   Authorization: mon_boss your-token-here
   ```

3. **Mettre à jour vos applications** :
   ```javascript
   headers: {
       'Authorization': 'mon_boss ' + token
   }
   ```

4. **Tester** :
   ```bash
   python test_api.py
   ```

Et voilà ! Votre API utilise maintenant le préfixe "API-Key" au lieu de "Bearer" ! 🎉 