from django import forms

from .models import Item, User_Review

class NewItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ('category', 'name', 'description', 'item_type', 'price', 'publication_date', 'author', 'image', 'created_by')

# clase de review form
class ReviewForm(forms.ModelForm):
    class Meta:
        model = User_Review
        fields = ['rating', 'comment']
        widgets = {
			'rating': forms.Select(choices=[(i, f"{i} ⭐") for i in range(1, 6)]),
			'comment': forms.Textarea(attrs={'class': 'w-full p-2 border rounded-md', 'placeholder': 'Write your review...'}),
		}