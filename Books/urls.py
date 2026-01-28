from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path, include

from .views import search_books


# aqui van todos los imports de los urls


urlpatterns = [
    path('', include('core.urls')),
    path('admin/', admin.site.urls),
    path('items/', include('item.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('search/', search_books, name='search_books'), # nueva ruta
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
