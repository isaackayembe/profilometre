#!/usr/bin/env python
"""
Script de test pour diagnostiquer les problèmes de Swagger
"""

import os
import sys
import django
from pathlib import Path

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'profilometre.settings')
django.setup()

from django.test import Client
from django.urls import reverse

def test_swagger_endpoints():
    """Test des endpoints Swagger"""
    client = Client()
    
    print("🔍 Test des endpoints Swagger...")
    print("=" * 50)
    
    # Test 1: Endpoint schema
    try:
        response = client.get('/api/schema/')
        print(f"✅ Schema endpoint: {response.status_code}")
        if response.status_code == 200:
            print(f"   Content-Type: {response.get('Content-Type', 'N/A')}")
            print(f"   Content length: {len(response.content)} bytes")
        else:
            print(f"   Erreur: {response.content.decode()[:200]}")
    except Exception as e:
        print(f"❌ Erreur schema endpoint: {e}")
    
    # Test 2: Endpoint Swagger UI
    try:
        response = client.get('/api/docs/')
        print(f"✅ Swagger UI endpoint: {response.status_code}")
        if response.status_code == 200:
            print(f"   Content-Type: {response.get('Content-Type', 'N/A')}")
            print(f"   Content length: {len(response.content)} bytes")
        else:
            print(f"   Erreur: {response.content.decode()[:200]}")
    except Exception as e:
        print(f"❌ Erreur Swagger UI endpoint: {e}")
    
    # Test 3: Endpoint ReDoc
    try:
        response = client.get('/api/redoc/')
        print(f"✅ ReDoc endpoint: {response.status_code}")
        if response.status_code == 200:
            print(f"   Content-Type: {response.get('Content-Type', 'N/A')}")
            print(f"   Content length: {len(response.content)} bytes")
        else:
            print(f"   Erreur: {response.content.decode()[:200]}")
    except Exception as e:
        print(f"❌ Erreur ReDoc endpoint: {e}")

def test_django_config():
    """Test de la configuration Django"""
    print("\n🔧 Test de la configuration Django...")
    print("=" * 50)
    
    from django.conf import settings
    
    # Vérifier les apps installées
    print(f"✅ Apps installées: {len(settings.INSTALLED_APPS)}")
    if 'drf_spectacular' in settings.INSTALLED_APPS:
        print("   ✅ drf_spectacular est installé")
    else:
        print("   ❌ drf_spectacular n'est pas installé")
    
    # Vérifier la configuration DRF
    print(f"✅ Configuration DRF: {settings.REST_FRAMEWORK.get('DEFAULT_SCHEMA_CLASS', 'Non configuré')}")
    
    # Vérifier la configuration Spectacular
    if hasattr(settings, 'SPECTACULAR_SETTINGS'):
        print(f"✅ Configuration Spectacular: {len(settings.SPECTACULAR_SETTINGS)} paramètres")
        print(f"   SERVE_INCLUDE_SCHEMA: {settings.SPECTACULAR_SETTINGS.get('SERVE_INCLUDE_SCHEMA', 'Non défini')}")
    else:
        print("   ❌ SPECTACULAR_SETTINGS non configuré")

if __name__ == "__main__":
    print("🚀 Diagnostic Swagger - Profilometre")
    print("=" * 50)
    
    test_django_config()
    test_swagger_endpoints()
    
    print("\n📋 Résumé:")
    print("1. Vérifiez que le serveur Django est démarré")
    print("2. Accédez à http://localhost:8000/api/docs/")
    print("3. Si problème persiste, vérifiez la console du navigateur")
    print("4. Vérifiez les logs Django pour les erreurs") 