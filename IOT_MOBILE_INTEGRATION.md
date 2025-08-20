# 🔐 Guide d'Intégration IoT & Mobile - JWT Sécurisé

## 🎯 Vue d'ensemble

Votre API Profilometre utilise maintenant **JWT (JSON Web Tokens)** avec refresh tokens pour une sécurité maximale. Voici comment intégrer vos équipements IoT et applications mobiles.

---

## 🔑 Endpoints d'Authentification JWT

### **1. Obtenir les Tokens (Connexion)**
```http
POST /api/token/
Content-Type: application/json

{
    "username": "votre_email@example.com",
    "password": "votre_mot_de_passe"
}
```

**Réponse :**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### **2. Rafraîchir le Token d'Accès**
```http
POST /api/token/refresh/
Content-Type: application/json

{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Réponse :**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### **3. Vérifier un Token**
```http
POST /api/token/verify/
Content-Type: application/json

{
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

---

## 📱 Intégration Mobile (React Native, Flutter, etc.)

### **React Native**
```javascript
// Configuration JWT
const API_BASE_URL = 'http://localhost:8000';

// Connexion et obtention des tokens
const login = async (email, password) => {
    try {
        const response = await fetch(`${API_BASE_URL}/api/token/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: email,
                password: password
            })
        });
        
        const data = await response.json();
        
        // Stocker les tokens
        await AsyncStorage.setItem('access_token', data.access);
        await AsyncStorage.setItem('refresh_token', data.refresh);
        
        return data;
    } catch (error) {
        console.error('Erreur de connexion:', error);
        throw error;
    }
};

// Fonction pour rafraîchir le token
const refreshToken = async () => {
    try {
        const refresh = await AsyncStorage.getItem('refresh_token');
        
        const response = await fetch(`${API_BASE_URL}/api/token/refresh/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                refresh: refresh
            })
        });
        
        const data = await response.json();
        
        // Mettre à jour le token d'accès
        await AsyncStorage.setItem('access_token', data.access);
        
        return data.access;
    } catch (error) {
        console.error('Erreur de refresh:', error);
        // Rediriger vers la page de connexion
        throw error;
    }
};

// Fonction pour appeler les APIs protégées
const callProtectedAPI = async (endpoint, options = {}) => {
    try {
        const accessToken = await AsyncStorage.getItem('access_token');
        
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            ...options,
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json',
                ...options.headers,
            },
        });
        
        // Si le token a expiré, essayer de le rafraîchir
        if (response.status === 401) {
            const newToken = await refreshToken();
            
            // Réessayer avec le nouveau token
            const retryResponse = await fetch(`${API_BASE_URL}${endpoint}`, {
                ...options,
                headers: {
                    'Authorization': `Bearer ${newToken}`,
                    'Content-Type': 'application/json',
                    ...options.headers,
                },
            });
            
            return retryResponse.json();
        }
        
        return response.json();
    } catch (error) {
        console.error('Erreur API:', error);
        throw error;
    }
};

// Exemple d'utilisation
const getUserProfile = () => callProtectedAPI('/api/auth/profile/');
const sendData = (data) => callProtectedAPI('/api/send/data/', {
    method: 'POST',
    body: JSON.stringify(data)
});
```

### **Flutter/Dart**
```dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class JWTService {
  static const String baseUrl = 'http://localhost:8000';
  
  // Connexion
  static Future<Map<String, dynamic>> login(String email, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/token/'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({
        'username': email,
        'password': password,
      }),
    );
    
    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      
      // Stocker les tokens
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('access_token', data['access']);
      await prefs.setString('refresh_token', data['refresh']);
      
      return data;
    } else {
      throw Exception('Échec de la connexion');
    }
  }
  
  // Rafraîchir le token
  static Future<String> refreshToken() async {
    final prefs = await SharedPreferences.getInstance();
    final refresh = prefs.getString('refresh_token');
    
    final response = await http.post(
      Uri.parse('$baseUrl/api/token/refresh/'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({'refresh': refresh}),
    );
    
    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      await prefs.setString('access_token', data['access']);
      return data['access'];
    } else {
      throw Exception('Échec du refresh token');
    }
  }
  
  // Appel API protégée
  static Future<Map<String, dynamic>> callProtectedAPI(String endpoint, {Map<String, dynamic>? data}) async {
    final prefs = await SharedPreferences.getInstance();
    String accessToken = prefs.getString('access_token') ?? '';
    
    final response = await http.post(
      Uri.parse('$baseUrl$endpoint'),
      headers: {
        'Authorization': 'Bearer $accessToken',
        'Content-Type': 'application/json',
      },
      body: data != null ? json.encode(data) : null,
    );
    
    if (response.statusCode == 401) {
      // Token expiré, essayer de le rafraîchir
      accessToken = await refreshToken();
      
      final retryResponse = await http.post(
        Uri.parse('$baseUrl$endpoint'),
        headers: {
          'Authorization': 'Bearer $accessToken',
          'Content-Type': 'application/json',
        },
        body: data != null ? json.encode(data) : null,
      );
      
      return json.decode(retryResponse.body);
    }
    
    return json.decode(response.body);
  }
}
```

---

## 🔌 Intégration IoT (Arduino, ESP32, Raspberry Pi, etc.)

### **Arduino/ESP32 (C++)**
```cpp
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// Configuration WiFi
const char* ssid = "Votre_WiFi";
const char* password = "Votre_Mot_De_Passe";

// Configuration API
const char* apiBaseUrl = "http://localhost:8000";
String accessToken = "";
String refreshToken = "";

// Connexion WiFi
void connectToWiFi() {
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.println("Connexion WiFi...");
    }
    Serial.println("WiFi connecté!");
}

// Connexion à l'API
bool loginToAPI() {
    HTTPClient http;
    http.begin(String(apiBaseUrl) + "/api/token/");
    http.addHeader("Content-Type", "application/json");
    
    // Données de connexion (à adapter selon vos besoins)
    String loginData = "{\"username\":\"iot_device@example.com\",\"password\":\"device_password\"}";
    
    int httpResponseCode = http.POST(loginData);
    
    if (httpResponseCode == 200) {
        String response = http.getString();
        
        // Parser la réponse JSON
        DynamicJsonDocument doc(1024);
        deserializeJson(doc, response);
        
        accessToken = doc["access"].as<String>();
        refreshToken = doc["refresh"].as<String>();
        
        Serial.println("Connexion réussie!");
        return true;
    } else {
        Serial.println("Échec de la connexion: " + String(httpResponseCode));
        return false;
    }
    
    http.end();
}

// Rafraîchir le token
bool refreshAccessToken() {
    HTTPClient http;
    http.begin(String(apiBaseUrl) + "/api/token/refresh/");
    http.addHeader("Content-Type", "application/json");
    
    String refreshData = "{\"refresh\":\"" + refreshToken + "\"}";
    
    int httpResponseCode = http.POST(refreshData);
    
    if (httpResponseCode == 200) {
        String response = http.getString();
        
        DynamicJsonDocument doc(1024);
        deserializeJson(doc, response);
        
        accessToken = doc["access"].as<String>();
        Serial.println("Token rafraîchi!");
        return true;
    } else {
        Serial.println("Échec du refresh: " + String(httpResponseCode));
        return false;
    }
    
    http.end();
}

// Envoyer des données à l'API
bool sendDataToAPI(float temperature, float humidity, float accelerometer) {
    HTTPClient http;
    http.begin(String(apiBaseUrl) + "/api/send/data/");
    http.addHeader("Content-Type", "application/json");
    http.addHeader("Authorization", "Bearer " + accessToken);
    
    // Préparer les données
    DynamicJsonDocument doc(512);
    doc["temperature"] = temperature;
    doc["humidite"] = humidity;
    doc["accelerometre"] = accelerometer;
    doc["timestamp"] = millis();
    
    String jsonData;
    serializeJson(doc, jsonData);
    
    int httpResponseCode = http.POST(jsonData);
    
    if (httpResponseCode == 200) {
        Serial.println("Données envoyées avec succès!");
        return true;
    } else if (httpResponseCode == 401) {
        // Token expiré, essayer de le rafraîchir
        if (refreshAccessToken()) {
            // Réessayer avec le nouveau token
            http.addHeader("Authorization", "Bearer " + accessToken);
            httpResponseCode = http.POST(jsonData);
            
            if (httpResponseCode == 200) {
                Serial.println("Données envoyées après refresh!");
                return true;
            }
        }
    }
    
    Serial.println("Échec envoi: " + String(httpResponseCode));
    return false;
}

void setup() {
    Serial.begin(115200);
    connectToWiFi();
    
    // Connexion initiale à l'API
    if (!loginToAPI()) {
        Serial.println("Impossible de se connecter à l'API!");
        return;
    }
}

void loop() {
    // Simuler des lectures de capteurs
    float temperature = random(20, 30);  // 20-30°C
    float humidity = random(40, 80);     // 40-80%
    float accelerometer = random(0, 100); // 0-100
    
    // Envoyer les données
    sendDataToAPI(temperature, humidity, accelerometer);
    
    delay(5000);  // Attendre 5 secondes
}
```

### **Python (Raspberry Pi)**
```python
import requests
import json
import time
from datetime import datetime

class IoTDevice:
    def __init__(self, api_base_url, username, password):
        self.api_base_url = api_base_url
        self.username = username
        self.password = password
        self.access_token = None
        self.refresh_token = None
        
    def login(self):
        """Connexion et obtention des tokens"""
        try:
            response = requests.post(
                f"{self.api_base_url}/api/token/",
                json={
                    "username": self.username,
                    "password": self.password
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data["access"]
                self.refresh_token = data["refresh"]
                print("Connexion réussie!")
                return True
            else:
                print(f"Échec de la connexion: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Erreur de connexion: {e}")
            return False
    
    def refresh_token(self):
        """Rafraîchir le token d'accès"""
        try:
            response = requests.post(
                f"{self.api_base_url}/api/token/refresh/",
                json={"refresh": self.refresh_token}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data["access"]
                print("Token rafraîchi!")
                return True
            else:
                print(f"Échec du refresh: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Erreur de refresh: {e}")
            return False
    
    def send_data(self, temperature, humidity, accelerometer):
        """Envoyer des données à l'API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            data = {
                "temperature": temperature,
                "humidite": humidity,
                "accelerometre": accelerometer,
                "timestamp": datetime.now().isoformat()
            }
            
            response = requests.post(
                f"{self.api_base_url}/api/send/data/",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                print("Données envoyées avec succès!")
                return True
            elif response.status_code == 401:
                # Token expiré, essayer de le rafraîchir
                if self.refresh_token():
                    # Réessayer avec le nouveau token
                    headers["Authorization"] = f"Bearer {self.access_token}"
                    response = requests.post(
                        f"{self.api_base_url}/api/send/data/",
                        headers=headers,
                        json=data
                    )
                    
                    if response.status_code == 200:
                        print("Données envoyées après refresh!")
                        return True
            
            print(f"Échec envoi: {response.status_code}")
            return False
            
        except Exception as e:
            print(f"Erreur d'envoi: {e}")
            return False

# Exemple d'utilisation
if __name__ == "__main__":
    device = IoTDevice(
        api_base_url="http://localhost:8000",
        username="iot_device@example.com",
        password="device_password"
    )
    
    # Connexion initiale
    if not device.login():
        exit(1)
    
    # Boucle principale
    while True:
        # Simuler des lectures de capteurs
        import random
        temperature = random.uniform(20, 30)
        humidity = random.uniform(40, 80)
        accelerometer = random.uniform(0, 100)
        
        # Envoyer les données
        device.send_data(temperature, humidity, accelerometer)
        
        time.sleep(5)  # Attendre 5 secondes
```

---

## 🔒 Sécurité et Bonnes Pratiques

### **1. Stockage Sécurisé des Tokens**
- **Mobile** : Utiliser le Keychain (iOS) ou Keystore (Android)
- **IoT** : Stocker en mémoire volatile quand possible
- **Web** : Utiliser HttpOnly cookies pour le refresh token

### **2. Gestion des Erreurs**
- Toujours gérer les erreurs 401 (token expiré)
- Implémenter une logique de retry avec refresh
- Logger les tentatives d'accès non autorisées

### **3. Configuration de Production**
```python
# Dans settings.py pour la production
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),  # Plus court en production
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),    # Plus long pour l'expérience utilisateur
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': os.environ.get('SECRET_KEY'),  # Utiliser une variable d'environnement
}
```

### **4. Monitoring**
- Surveiller les tentatives de refresh token
- Alerter en cas d'activité suspecte
- Logs détaillés pour le debugging

---

## 🚀 Test de l'Intégration

### **1. Test avec curl**
```bash
# Connexion
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"test@example.com","password":"password123"}'

# Utiliser le token
curl -X GET http://localhost:8000/api/auth/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Rafraîchir le token
curl -X POST http://localhost:8000/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh":"YOUR_REFRESH_TOKEN"}'
```

### **2. Test avec Postman**
1. Importez la collection depuis : `http://localhost:8000/api/schema/`
2. Configurez l'URL de base : `http://localhost:8000`
3. Testez les endpoints JWT

---

## 📞 Support

- **Documentation API** : `http://localhost:8000/api/docs/`
- **Schéma OpenAPI** : `http://localhost:8000/api/schema/`
- **Guide de sécurité** : `ALLAUTH_SECURITY_GUIDE.md`

---

**🔐 Votre API est maintenant prête pour l'intégration IoT et mobile sécurisée avec JWT !** 