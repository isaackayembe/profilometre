#!/usr/bin/env python
"""
Script de test pour l'API Profilometre
Ce script teste tous les endpoints d'authentification
"""

import requests
import json
import sys
from urllib.parse import urljoin

class ProfilometreAPITester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.token = None
        self.user = None
        
    def print_result(self, test_name, success, message=""):
        """Affiche le résultat d'un test"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if message:
            print(f"   {message}")
        return success
    
    def test_server_connection(self):
        """Test de connexion au serveur"""
        try:
            response = requests.get(self.base_url)
            return self.print_result("Connexion au serveur", response.status_code == 200)
        except requests.exceptions.ConnectionError:
            return self.print_result("Connexion au serveur", False, "Serveur non accessible")
    
    def test_api_docs(self):
        """Test de la documentation API"""
        try:
            response = requests.get(urljoin(self.base_url, "/api/docs/"))
            return self.print_result("Documentation API", response.status_code == 200)
        except requests.exceptions.ConnectionError:
            return self.print_result("Documentation API", False, "Documentation non accessible")
    
    def test_signup(self):
        """Test d'inscription"""
        signup_data = {
            "email": "test@example.com",
            "password1": "testpassword123",
            "password2": "testpassword123",
            "first_name": "Test",
            "last_name": "User"
        }
        
        try:
            response = requests.post(
                urljoin(self.base_url, "/api/auth/signup/"),
                json=signup_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 201:
                data = response.json()
                self.token = data.get("token")
                self.user = data.get("user")
                return self.print_result("Inscription", True, f"Utilisateur créé: {data.get('user', {}).get('email')}")
            else:
                error_msg = response.json().get("error", "Erreur inconnue")
                return self.print_result("Inscription", False, error_msg)
        except Exception as e:
            return self.print_result("Inscription", False, str(e))
    
    def test_login(self):
        """Test de connexion"""
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        try:
            response = requests.post(
                urljoin(self.base_url, "/api/auth/login/"),
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("token")
                self.user = data.get("user")
                return self.print_result("Connexion", True, f"Utilisateur connecté: {data.get('user', {}).get('email')}")
            else:
                error_msg = response.json().get("error", "Erreur inconnue")
                return self.print_result("Connexion", False, error_msg)
        except Exception as e:
            return self.print_result("Connexion", False, str(e))
    
    def test_profile(self):
        """Test de récupération du profil"""
        if not self.token:
            return self.print_result("Profil", False, "Token non disponible")
        
        try:
            response = requests.get(
                urljoin(self.base_url, "/api/auth/profile/"),
                headers={"Authorization": f"mon_boss {self.token}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                return self.print_result("Profil", True, f"Profil récupéré: {data.get('email')}")
            else:
                error_msg = response.json().get("error", "Erreur inconnue")
                return self.print_result("Profil", False, error_msg)
        except Exception as e:
            return self.print_result("Profil", False, str(e))
    
    def test_password_reset_request(self):
        """Test de demande de réinitialisation de mot de passe"""
        reset_data = {
            "email": "test@example.com"
        }
        
        try:
            response = requests.post(
                urljoin(self.base_url, "/api/auth/password-reset/"),
                json=reset_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                return self.print_result("Demande réinitialisation mot de passe", True)
            else:
                error_msg = response.json().get("error", "Erreur inconnue")
                return self.print_result("Demande réinitialisation mot de passe", False, error_msg)
        except Exception as e:
            return self.print_result("Demande réinitialisation mot de passe", False, str(e))
    
    def test_logout(self):
        """Test de déconnexion"""
        if not self.token:
            return self.print_result("Déconnexion", False, "Token non disponible")
        
        try:
            response = requests.post(
                urljoin(self.base_url, "/api/auth/logout/"),
                headers={"Authorization": f"mon_boss {self.token}"}
            )
            
            if response.status_code == 200:
                self.token = None
                self.user = None
                return self.print_result("Déconnexion", True)
            else:
                error_msg = response.json().get("error", "Erreur inconnue")
                return self.print_result("Déconnexion", False, error_msg)
        except Exception as e:
            return self.print_result("Déconnexion", False, str(e))
    
    def run_all_tests(self):
        """Exécute tous les tests"""
        print("🧪 Tests de l'API Profilometre")
        print("=" * 50)
        
        tests = [
            ("Connexion au serveur", self.test_server_connection),
            ("Documentation API", self.test_api_docs),
            ("Inscription", self.test_signup),
            ("Connexion", self.test_login),
            ("Profil utilisateur", self.test_profile),
            ("Demande réinitialisation mot de passe", self.test_password_reset_request),
            ("Déconnexion", self.test_logout),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            if test_func():
                passed += 1
            print()
        
        print("=" * 50)
        print(f"📊 Résultats: {passed}/{total} tests réussis")
        
        if passed == total:
            print("🎉 Tous les tests sont passés avec succès!")
            return True
        else:
            print("⚠️  Certains tests ont échoué. Vérifiez la configuration.")
            return False

def main():
    """Fonction principale"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test de l'API Profilometre")
    parser.add_argument("--url", default="http://localhost:8000", 
                       help="URL de base de l'API (défaut: http://localhost:8000)")
    
    args = parser.parse_args()
    
    tester = ProfilometreAPITester(args.url)
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 