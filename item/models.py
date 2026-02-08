from django.contrib.auth.models import User
from django.db import models
from django.db.models import Avg

class Category(models.Model):
    name = models.CharField(max_length=255)

	# para que salga plural el nombre de la db
	# ordering para que los nombres esten por orden alfabetico
    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'Categories'

	# para que salgan los nombres en el admin page del db
    def __str__(self):
        return self.name


class Item(models.Model):
    category = models.ForeignKey(Category, related_name='items', on_delete=models.CASCADE, null=True, blank=True)
    # nombre del articulo
    name = models.CharField(max_length=255)
    # descripcion del aticulo
    description = models.TextField(blank=True, null=True)
    # catregoria de tipo de articulo, libro, comic, manga
    ITEM_TYPES = [
		('books', 'Book'),
		('comics', 'Comics'),
		('manga', 'Manga')
	]
    item_type = models.CharField(max_length=20, choices=ITEM_TYPES, default='book')
    # precio del articulo
    price = models.FloatField()
    # fecha de publicacion
    publication_date = models.DateField(blank=True, null=True)
    # nombre de author
    author = models.CharField(max_length=255, blank=True, null=True)
    # imagen del articulo
    image = models.ImageField(upload_to='items/', blank=True, null=True)

    created_by = models.ForeignKey(User, related_name='items', on_delete=models.CASCADE, null=True, blank=True)    # fields para la creacion y actualizacion
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    #rating del articulo
    rating = models.FloatField(default=0)
    # marcar si el user ya leyo el libro
    users_read = models.ManyToManyField(User, related_name="read_books", blank=True)
    # marcar si el user ya lo tiene en la lista de leer
    readlisted_by = models.ManyToManyField(User, related_name="readlist_books", blank=True)
    google_id = models.CharField(max_length=50, blank=True, null=True, unique=True)

# new
    def user_rating(self):
        # Calcular el promedio de las calificaciones de las reseñas
        reviews = self.reviews.all()
        if reviews.exists():
            return reviews.aggregate(Avg('rating'))['rating__avg']
        return 0

    def is_local(self):
        return self.price != 0

    def __str__(self):
        return self.name

#new
class User_Review(models.Model):
    item = models.ForeignKey(Item, related_name="reviews", on_delete=models.CASCADE, null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} for {self.item.name}"
