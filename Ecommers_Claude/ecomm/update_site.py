import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecomm.settings')
django.setup()

from django.contrib.sites.models import Site

def update_site():
    try:
        site = Site.objects.get(id=1)
        site.domain = '127.0.0.1:8000'
        site.name = 'My E-com'
        site.save()
        print(f"Updated Site ID 1 to: {site.domain}")
    except Site.DoesNotExist:
        Site.objects.create(id=1, domain='127.0.0.1:8000', name='My E-com')
        print("Created Site ID 1: 127.0.0.1:8000")

if __name__ == '__main__':
    update_site()
