#!/usr/bin/env python
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'profilometre.settings')
django.setup()

from django.contrib.sites.models import Site

def setup_default_site():
    """Configure le site par défaut pour Allauth"""
    try:
        # Récupérer ou créer le site par défaut
        site, created = Site.objects.get_or_create(
            id=1,
            defaults={
                'domain': 'localhost:8000',
                'name': 'Profilometre Local'
            }
        )
        
        if created:
            print(f"Site créé: {site.name} ({site.domain})")
        else:
            # Mettre à jour le site existant
            site.domain = 'localhost:8000'
            site.name = 'Profilometre Local'
            site.save()
            print(f"Site mis à jour: {site.name} ({site.domain})")
            
    except Exception as e:
        print(f"Erreur lors de la configuration du site: {e}")

if __name__ == '__main__':
    setup_default_site() 