from .models import Category

def global_categories(request):
    """
    Context processor to make categories available globally for the navbar dropdown.
    Fetches parent categories (those with no parent).
    """
    return {
        'navbar_categories': Category.objects.filter(parent__isnull=True).prefetch_related('children')
    }
