import requests
from item.models import Item, Category
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

# codigo de search sin cache
# def search_books(request):
#     query = request.GET.get('query', '')
#     items = []

#     # Aquí podrías agregar libros locales si quieres, usando tu modelo Item
#     # Pero para simplificar, dejaremos solo Google Books

#     if query:
#         api_url = f'https://www.googleapis.com/books/v1/volumes?q={query}&key={settings.GOOGLE_BOOKS_API_KEY}'
#         response = requests.get(api_url)

#         if response.status_code == 200:
#             data = response.json()
#             google_books = data.get('items', [])
#             for book in google_books:
#                 volume_info = book.get('volumeInfo', {})
#                 items.append({
#                     'id': book.get('id'),
#                     'title': volume_info.get('title', 'No Title'),
#                     'authors': ', '.join(volume_info.get('authors', ['Unknown'])),
#                     'image': volume_info.get('imageLinks', {}).get('thumbnail', '/static/images/default_book.png'),
#                     'description': volume_info.get('description', ''),
#                     'google_id': book.get('id'),
#                 })
#             book_cache[query] = items

#     return render(request, 'item/browse.html', {'items': items, 'query': query})

book_cache = {}
book_detail_cache = {}

def search_books(request):
    query = request.GET.get('query', '').strip()
    items = []

    # Traemos categorías locales SIEMPRE
    categories = Category.objects.all()
    category_id = request.GET.get('category')

    # Si no hay búsqueda, renderizamos vacío pero con sidebar
    if not query:
        return render(request, 'item/browse.html', {
            'items': items,
            'query': query,
            'categories': categories,
            'category_id': category_id,
        })

    # Usar cache si existe
    if query in book_cache:
        items = book_cache[query]
    else:
        api_url = (
            f"https://www.googleapis.com/books/v1/volumes"
            f"?q={query}"
            f"&maxResults=20"
            f"&key={settings.GOOGLE_BOOKS_API_KEY}"
        )

        response = requests.get(api_url)

        if response.status_code == 200:
            data = response.json()
            google_books = data.get('items', [])

            for book in google_books:
                volume_info = book.get('volumeInfo', {})

                items.append({
                    'google_id': book.get('id'),
                    'title': volume_info.get('title', 'No Title'),
                    'authors': ', '.join(volume_info.get('authors', ['Unknown'])),
                    'categories': ', '.join(volume_info.get('categories', ['Unknown'])),
                    'image': volume_info.get('imageLinks', {}).get(
                        'thumbnail',
                        '/static/images/default_book.png'
                    ),
                    'description': volume_info.get('description', ''),
                })

            # Guardamos resultados en cache
            book_cache[query] = items

    return render(request, 'item/browse.html', {
        'items': items,
        'query': query,
        'categories': categories,
        'category_id': category_id,
    })


def google_book_detail(request):
    book_id = request.GET.get('id')
    if not book_id:
        return redirect('search_books')

    # Revisamos cache
    if book_id in book_detail_cache:
        book = book_detail_cache[book_id]
        error = None
    else:
        url = f"https://www.googleapis.com/books/v1/volumes/{book_id}?key={settings.GOOGLE_BOOKS_API_KEY}"
        response = requests.get(url)

        if response.status_code != 200:
            book = None
            error = 'Could not fetch book details from Google Books.'
        else:
            data = response.json()
            volume_info = data.get('volumeInfo', {})

            book = {
                'title': volume_info.get('title', 'No Title'),
                'authors': ', '.join(volume_info.get('authors', ['Unknown'])),
                'published_date': volume_info.get('publishedDate', 'N/A'),
                'publisher': volume_info.get('publisher', 'N/A'),
                'categories': ', '.join(volume_info.get('categories', [])) if volume_info.get('categories') else 'General',
                'page_count': volume_info.get('pageCount', 'N/A'),
                'description': volume_info.get('description', 'No description available.'),
                'image': volume_info.get('imageLinks', {}).get('thumbnail', '/static/images/default_book.png'),
                'preview_link': volume_info.get('previewLink'),
                'google_id': data.get('id'),
            }
            book_detail_cache[book_id] = book
            error = None

    # Creamos o buscamos el Item local
    item, created = Item.objects.get_or_create(
        google_id=book_id,
        defaults={
            'name': book['title'],
            'author': book['authors'],
            'description': book['description'],
            'image': book['image'],
            'price': 0,
        }
    )

    # Related books (hasta 4 libros de cualquier categoría del libro)
    related_books = []
    seen_ids = set([book_id])
    categories = book['categories'].split(',')

    for category in categories:
        category = category.strip()
        related_url = (
            f"https://www.googleapis.com/books/v1/volumes"
            f"?q=subject:{category}"
            f"&maxResults=10"
            f"&key={settings.GOOGLE_BOOKS_API_KEY}"
        )
        response = requests.get(related_url)
        if response.status_code != 200:
            continue

        data = response.json().get('items', [])
        for b in data:
            google_id = b.get('id')
            if not google_id or google_id in seen_ids:
                continue

            info = b.get('volumeInfo', {})
            related_books.append({
                'google_id': google_id,
                'title': info.get('title', 'No title'),
                'authors': ', '.join(info.get('authors', ['Unknown'])),
                'categories': ', '.join(info.get('categories', [])) if info.get('categories') else 'General',
                'image': info.get('imageLinks', {}).get('thumbnail', '/static/images/default_book.png')
            })
            seen_ids.add(google_id)

            if len(related_books) >= 4:
                break
        if len(related_books) >= 4:
            break

    return render(request, 'google_book_detail.html', {
        'book': book,
        'item': item,
        'reviews': item.reviews.all() if hasattr(item, 'reviews') else [],
        'error': error,
        'related_books': related_books
    })





# Suponiendo que ya tienes un diccionario global
# no tiene lo de los reviews
# book_detail_cache = {}

# @login_required
# def google_book_detail(request):
#     book_id = request.GET.get('id')
#     if not book_id:
#         return redirect('search_books')

#     # Revisamos cache
#     if book_id in book_detail_cache:
#         book = book_detail_cache[book_id]
#         error = None
#     else:
#         url = f"https://www.googleapis.com/books/v1/volumes/{book_id}?key={settings.GOOGLE_BOOKS_API_KEY}"
#         response = requests.get(url)

#         if response.status_code != 200:
#             book = None
#             error = 'Could not fetch book details from Google Books.'
#         else:
#             data = response.json()
#             volume_info = data.get('volumeInfo', {})

#             book = {
#                 'title': volume_info.get('title', 'No Title'),
#                 'authors': ', '.join(volume_info.get('authors', ['Unknown'])),
#                 'published_date': volume_info.get('publishedDate', 'N/A'),
#                 'publisher': volume_info.get('publisher', 'N/A'),
#                 'categories': ', '.join(volume_info.get('categories', [])) if volume_info.get('categories') else 'N/A',
#                 'page_count': volume_info.get('pageCount', 'N/A'),
#                 'description': volume_info.get('description', 'No description available.'),
#                 'image': volume_info.get('imageLinks', {}).get('thumbnail', '/static/images/default_book.png'),
#                 'preview_link': volume_info.get('previewLink'),
#                 'google_id': data.get('id'),
#             }

#             # Guardamos en cache
#             book_detail_cache[book_id] = book
#             error = None

#     # creamos o buscamos el Item local ---
#     item, created = Item.objects.get_or_create(
#         google_id=book_id,
#         defaults={
#             'name': book['title'],
#             'author': book['authors'],
#             'description': book['description'],
#             'image': book['image'],
#             'price': 0,  # por si pide el precio
#         }
#     )

#     reviews = item.reviews.all()
#     user_rating = item.user_rating() if hasattr(item, 'user_rating') else None

#     return render(request, 'google_book_detail.html', {
#         'book': book,
#         'item': item,
#         'reviews': reviews,
#         'user_rating': user_rating,
#         'error': error
#     })




# con cache pero sin el review prueba 1
# def google_book_detail(request):
#     book_id = request.GET.get('id')
#     if not book_id:
#         return redirect('search_books')

#     # Revisamos cache de detalles
#     if book_id in book_detail_cache:
#         book = book_detail_cache[book_id]
#         error = None
#     else:
#         url = f"https://www.googleapis.com/books/v1/volumes/{book_id}?key={settings.GOOGLE_BOOKS_API_KEY}"
#         response = requests.get(url)

#         if response.status_code != 200:
#             book = None
#             error = 'Could not fetch book details from Google Books.'
#         else:
#             data = response.json()
#             volume_info = data.get('volumeInfo', {})

#             book = {
#                 'title': volume_info.get('title', 'No Title'),
#                 'authors': ', '.join(volume_info.get('authors', ['Unknown'])),
#                 'published_date': volume_info.get('publishedDate', 'N/A'),
#                 'publisher': volume_info.get('publisher', 'N/A'),
#                 'categories': ', '.join(volume_info.get('categories', [])) if volume_info.get('categories') else 'N/A',
#                 'page_count': volume_info.get('pageCount', 'N/A'),
#                 'description': volume_info.get('description', 'No description available.'),
#                 'image': volume_info.get('imageLinks', {}).get('thumbnail', '/static/images/default_book.png'),
#                 'preview_link': volume_info.get('previewLink'),
#                 'google_id': data.get('id'),
#             }

#             # Guardamos en cache
#             book_detail_cache[book_id] = book
#             error = None

#     return render(request, 'google_book_detail.html', {'book': book, 'error': error})


# el regular
# def google_book_detail(request):
#     book_id = request.GET.get('id')
#     if not book_id:
#         return redirect('search_books')

#     url = f"https://www.googleapis.com/books/v1/volumes/{book_id}"
#     response = requests.get(url)
#     print(response.json())

#     if response.status_code != 200:
#         return render(request, 'google_book_detail.html', {
#             'book': None,
#             'error': 'Could not fetch book details from Google Books.'
#         })

#     data = response.json()
#     volume_info = data.get('volumeInfo', {})

#     # Diccionario seguro con fallbacks
#     book = {
#         'title': volume_info.get('title', 'No Title'),
#         'authors': ', '.join(volume_info.get('authors', ['Unknown'])),
#         'published_date': volume_info.get('publishedDate', 'N/A'),
#         'publisher': volume_info.get('publisher', 'N/A'),
#         'categories': ', '.join(volume_info.get('categories', [])) if volume_info.get('categories') else 'N/A',
#         'page_count': volume_info.get('pageCount', 'N/A'),
#         'description': volume_info.get('description', 'No description available.'),
#         'image': volume_info.get('imageLinks', {}).get('thumbnail', '/static/images/default_book.png'),
#         'preview_link': volume_info.get('previewLink'),
#     }

#     return render(request, 'google_book_detail.html', {'book': book, 'error': None})



# mockup para ver si el template funciona, me salia vacio el template en la pagina
# from django.shortcuts import render, redirect

# def google_book_detail(request):
#     # Obtenemos el id (no lo usamos en el mock)
#     book_id = request.GET.get('id')
#     if not book_id:
#         return redirect('search_books')

#     # Datos simulados de un libro de Google Books
#     book = {
#         'title': 'Star Wars: A New Hope',
#         'authors': 'George Lucas',
#         'published_date': '1977-05-25',
#         'publisher': 'Lucasfilm',
#         'categories': 'Sci-Fi, Adventure',
#         'page_count': 121,
#         'description': 'A space opera about the battle between the Empire and the Rebels. Follow the adventures of Luke Skywalker, Princess Leia, and Han Solo.',
#         'image': 'https://via.placeholder.com/200x300.png?text=Book+Cover', # puedes poner la portada real si quieres
#         'preview_link': 'https://books.google.com/',
#     }

#     return render(request, 'google_book_detail.html', {'book': book, 'error': None})
