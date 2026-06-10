from django import forms
from .models import Book, Category, Author, Publisher


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        exclude = ('slug', 'rating', 'reviews_count', 'created_at', 'updated_at')
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'publication_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
