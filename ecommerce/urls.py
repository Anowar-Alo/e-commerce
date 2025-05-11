from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.admin import admin_site

urlpatterns = [
    path('admin/', admin_site.urls),
    path('', include('core.urls', namespace='core')),
    path('products/', include('products.urls', namespace='products')),
    path('orders/', include('orders.urls', namespace='orders')),
    path('payments/', include('payments.urls', namespace='payments')),
    path('cart/', include('cart.urls', namespace='cart')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
