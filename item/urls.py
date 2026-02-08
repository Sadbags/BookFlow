from django.urls import path

from . import views

app_name = 'item'

urlpatterns = [
    path('', views.items, name='items'),
    path('new_item/', views.new_item, name='new_item'),
	path('book/<int:item_id>/', views.detail, name='detail'),
	#ruta para marcar mark as read
    path('mark-as-read/<int:item_id>/', views.mark_as_read, name='mark_as_read'),
    # Ruta para la página de detalles del libro
    path('<int:item_id>/', views.detail, name='detail'),
    # Ruta para agregar o quitar un libro de la readlist
    path('toggle_readlist/<int:item_id>/', views.toggle_readlist, name='toggle_readlist'),
    # Ruta para ver la readlist del usuario
    path('readlist/', views.readlist, name='readlist'),
    # ruta para enviar del readlista a la pagina del libro
    path('book/<int:book_id>/', views.detail, name='detail'),
    # ruta para el review de los libros
    path('<int:item_id>/review/', views.add_review, name='review'),
    # ruta para el detalles de libros de google books
    #path('google/', views.google_book_detail, name='google_book_detail'),
    path('add_google_to_read/<str:google_id>/', views.add_google_to_read, name='add_google_to_read'),
    path('add_google_to_readlist/<str:google_id>/', views.add_google_to_readlist, name='add_google_to_readlist'),
    #ruta de dashboard reviews detail
    path('dashboard/book/<int:item_id>/', views.dashboard_book_detail, name='dashboard_book_detail'),


]
