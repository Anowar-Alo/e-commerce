from django import forms
from .models import ProductReview

class ReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ['title', 'rating', 'comment', 'is_recommended']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5, 'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_recommended': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        } 