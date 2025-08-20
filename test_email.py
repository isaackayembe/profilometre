#!/usr/bin/env python
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'profilometre.settings')
django.setup()

from django.core.mail import send_mail
from django.contrib.auth.models import User
from allauth.account.models import EmailAddress

def test_email_sending():
    """Test d'envoi d'email"""
    print("=== Test d'envoi d'email ===")
    
    try:
        # Test d'envoi d'email simple
        send_mail(
            subject='Test Email Profilometre',
            message='Ceci est un test d\'email depuis Profilometre',
            from_email='test@profilometre.com',
            recipient_list=['test@example.com'],
            fail_silently=False,
        )
        print("✅ Email de test envoyé avec succès")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi d'email: {e}")

def check_email_settings():
    """Vérifier les paramètres email"""
    print("\n=== Paramètres Email ===")
    
    from django.conf import settings
    
    print(f"EMAIL_BACKEND: {getattr(settings, 'EMAIL_BACKEND', 'Non défini')}")
    print(f"EMAIL_HOST: {getattr(settings, 'EMAIL_HOST', 'Non défini')}")
    print(f"EMAIL_PORT: {getattr(settings, 'EMAIL_PORT', 'Non défini')}")
    print(f"EMAIL_USE_TLS: {getattr(settings, 'EMAIL_USE_TLS', 'Non défini')}")
    print(f"EMAIL_HOST_USER: {getattr(settings, 'EMAIL_HOST_USER', 'Non défini')}")
    print(f"DEFAULT_FROM_EMAIL: {getattr(settings, 'DEFAULT_FROM_EMAIL', 'Non défini')}")

def check_allauth_settings():
    """Vérifier les paramètres Allauth"""
    print("\n=== Paramètres Allauth ===")
    
    from django.conf import settings
    
    print(f"ACCOUNT_EMAIL_VERIFICATION: {getattr(settings, 'ACCOUNT_EMAIL_VERIFICATION', 'Non défini')}")
    print(f"ACCOUNT_LOGIN_METHODS: {getattr(settings, 'ACCOUNT_LOGIN_METHODS', 'Non défini')}")
    print(f"ACCOUNT_SIGNUP_FIELDS: {getattr(settings, 'ACCOUNT_SIGNUP_FIELDS', 'Non défini')}")

if __name__ == '__main__':
    check_email_settings()
    check_allauth_settings()
    test_email_sending() 