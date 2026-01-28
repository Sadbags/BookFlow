from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth.models import User


from item.models import Item

@login_required
def index(request):
    # obtiene el usuario que esta conectado
    user = request.user
    books_read = user.read_books.all()
    books_to_read = user.readlist_books.all()

    #if user.is_authenticated:
        # obtiene los libros leidos por el usuario
    #    books_read = user.read_books.all()
    #   bookmark = user.readlist_books.all()

    context = {
		'books_read': books_read,
        'bookmark': books_to_read,
	}
    return render(request, 'dashboard/index.html', context)