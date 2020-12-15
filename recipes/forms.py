from django import forms # import the forms library
from django.forms import ModelForm # This allows me to set up a ModelForm
from .models import AllRecipes # This is the class I need for ModelFOrm

class RecipeForm(forms.ModelForm):
    class Meta:
        model = AllRecipes
        fields = [
             
            'user_search_terms'
        ]

 
    


 
