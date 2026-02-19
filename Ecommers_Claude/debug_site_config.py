import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecomm.settings')
django.setup()

from myecom.models import SiteConfiguration

try:
    config = SiteConfiguration.get_solo()
    print(f"Site name: '{config.site_name}'")
    print(f"ID: {config.pk}")
    
    # Check if a config already existed with a different name
    configs = SiteConfiguration.objects.all()
    print(f"Total configs: {configs.count()}")
    for c in configs:
        print(f"Config {c.pk}: {c.site_name}")
        
except Exception as e:
    print(f"Error: {e}")
