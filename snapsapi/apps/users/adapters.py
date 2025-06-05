# users/adapters.py
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.sites.shortcuts import get_current_site
from allauth.socialaccount.models import SocialApp

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def get_app(self, request, provider, client_id=None):
        site = get_current_site(request)
        print(f"🔍 DEBUG: get_app() called for provider={provider}")
        print(f"🔍 Site: {site.id} - {site.domain}")

        apps = SocialApp.objects.filter(provider=provider, sites=site)
        print(f"🔍 Matching apps: {[a.id for a in apps]}")

        return super().get_app(request, provider, client_id)
