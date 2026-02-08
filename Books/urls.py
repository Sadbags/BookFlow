from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path, include
from . import views

from .views import search_books, google_book_detail



# aqui van todos los imports de los urls


urlpatterns = [
    path('', include('core.urls')),
    path('admin/', admin.site.urls),
    path('items/', include('item.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('search/', search_books, name='search_books'), # nueva ruta
    path('book/google/', google_book_detail, name='google_book_detail'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
