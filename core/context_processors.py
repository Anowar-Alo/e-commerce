from products.models import Category
from .models import SiteSettings

def categories(request):
    return {
        'categories': Category.objects.filter(is_active=True)
    }

def site_settings(request):
    return {
        'site_settings': SiteSettings.get_settings()
    } 