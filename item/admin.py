from django.contrib import admin

from .models import Category, Item, User_Review



class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'item', 'rating', 'created_at')  # Mostrar campos útiles en el listado
    list_filter = ('rating', 'created_at')  # Filtros por calificación o fecha
    search_fields = ('user__username', 'item__name')  # Buscar por nombre de usuario o nombre del artículo
    actions = ['delete_reviews']  # Acciones personalizadas, como eliminar comentarios

    # Definir la acción de eliminar comentarios
    def delete_reviews(self, request, queryset):
        queryset.delete()
    delete_reviews.short_description = "Delete selected reviews"

admin.site.register(User_Review, ReviewAdmin)
admin.site.register(Category)
admin.site.register(Item)