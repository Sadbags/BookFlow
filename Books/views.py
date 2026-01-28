# Books/views.py
import requests
from django.conf import settings
from django.shortcuts import render
from item.models import Item  # 🔑 importa tu modelo de libros locales

def search_books(request):
    query = request.GET.get('query', '')
    items = []

    # Libros locales, que ańadi como admin
    if query:
        local_books = Item.objects.filter(name__icontains=query)
        for book in local_books:
            items.append({
                'id': book.id,
                'name': book.name,
                'author': book.author,
                'image': book.image.url if book.image else '',
                'price': book.price,
            })

    # Libros de Google Books
    if query:
        api_url = f'https://www.googleapis.com/books/v1/volumes?q={query}&key={settings.GOOGLE_BOOKS_API_KEY}'
        response = requests.get(api_url)

        if response.status_code == 200:
            data = response.json()
            google_books = data.get('items', [])
            for book in google_books:
                volume_info = book.get('volumeInfo', {})
                items.append({
                    'id': book.get('id'),
                    'name': volume_info.get('title', 'No title'),
                    'author': ', '.join(volume_info.get('authors', ['Unknown'])),
                    'image': volume_info.get('imageLinks', {}).get('thumbnail', ''),
                    'price': 'N/A',
                })

    # Renderizamos todo junto
    return render(request, 'item/browse.html', {'items': items, 'query': query})
