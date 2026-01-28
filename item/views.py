# este es el file de views aqui van las funciones o clases que hacen las solicitudes http y devuelven respuestas.
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q

from .forms import NewItemForm, ReviewForm
from .models import Item, Category
from random import sample

# maneja la pagina de browse y el html de browse
def items(request):
    query = request.GET.get('query', '')
    category_id = request.GET.get('category', 0)
    categories = Category.objects.all()
    items = Item.objects.all()

	# si el articulo incluye una categoria, filtra los libros por esa categoria
    if category_id:
        items = items.filter(category_id=category_id)

	# busca el articulo por nombre o descripcion
    if query:
        items = items.filter(Q(name__icontains=query) | Q(description__icontains=query))

    return render(request, 'item/browse.html', {
		'items': items,
        'query': query,
        'categories': categories,
        'category_id': int(category_id),
	})

# maneja detalles de la pagina de libros, enseña el libro y los related books
@login_required
def detail(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    reviews = item.reviews.all()
    user_rating = item.user_rating()
    # esto hace que los libro en related cambien y no salgan los mismos
    related_items = list(Item.objects.filter(category=item.category).exclude(id=item_id))
    # enseña cantidad de libros
    if len(related_items) > 4:
        related_items = sample(related_items, 4)

    form = ReviewForm()  # Definirlo antes de entrar en el if

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.item = item
            review.user = request.user
            review.save()
            return redirect('item:detail', item_id=item.id)

    return render(request, 'item/detail.html', {
        'item': item,
        'related_items': related_items,
        'user_rating': user_rating,
        'form': form,
        'reviews': reviews,
    })


# funcion para el boton de mark as read
@login_required
def mark_as_read(request, item_id):
    item = get_object_or_404(Item, id=item_id)

    if item in request.user.read_books.all():
        request.user.read_books.remove(item)
    else:
        request.user.read_books.add(item)

    return redirect('item:detail', item_id=item.id)

# funcion para guardar los libros en la lista de readlist
@login_required
def toggle_readlist(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    user = request.user

    if item in user.readlist_books.all():
        user.readlist_books.remove(item)
    else:
        user.readlist_books.add(item)

    return redirect('item:detail', item_id=item.id)

def readlist(request):
    if request.user.is_authenticated:
        readlist_books = request.user.readlist_books.all()  # Obtén los libros de la lista de lectura del usuario
        return render(request, 'item/readlist.html', {'readlist_books': readlist_books})
    else:
        return redirect('core:login')


@login_required
def new_item(request):
    form = NewItemForm()

    return render(request, 'item/form.html', {
		'form': form,
		'title': 'New Item',
	})

# funcion para la pagina de review
@login_required
def add_review(request, item_id):
    item = get_object_or_404(Item, id=item_id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.item = item
            review.user = request.user
            review.save()

            # Recalcular la calificación del libro
            item.rating = item.user_rating()
            item.save()

            # Redirigir a la página del libro para ver la reseña
            return redirect('item:detail', item_id=item.id)

    return redirect('item:detail', item_id=item.id)
