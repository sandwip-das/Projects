from .models import SiteConfiguration

def site_configuration(request):
    """
    Context processor to make SiteConfiguration available in all templates.
    """
    try:
        config = SiteConfiguration.get_solo()
    except Exception:
        config = None
        
    return {'site_config': config}
