# Register your models here.

from django.contrib import admin
from django.apps import apps # this will allow me to auto-register all models not already registered (at the end)
 
from .models import SearchTerms
from .models import AllRecipes
from .models import AllContents


# Below, I am telling the Django admin site that we are using a custom class. It shows how to display the model in
# the admin site.
class RecipeAdmin(admin.ModelAdmin): # I think this overrides Admin defaults
	"""
	Here's where I customize Admin for the AllRecipes model
	"""
 
	
	list_display = ['url','anchortext', 'hyperlink', 'id', 'user_search_terms']
	list_filter = ('url', 'anchortext', 'hyperlink','id')
	search_fields = ('anchortext', 'hyperlink', 'id')
	list_max_show_all = 500
	list_per_page = 500


class SearchAdmin(admin.ModelAdmin): # I think this overrides Admin defaults
	"""
	Here's where I customize Admin for the SearchTerms model
	"""
	list_display = ['searchterm', 'id']
	list_filter = ('searchterm', 'id')
	list_max_show_all = 1000
	list_per_page = 1000



class AllContentsAdmin(admin.ModelAdmin):
	list_display = ['id','title', 'hyperlink', 'fullpost']	 
	search_fields = ('id', 'title', 'hyperlink', 'fullpost')
	list_max_show_all = 1000
	list_per_page = 1000


admin.site.register(AllRecipes, RecipeAdmin) 
admin.site.register(SearchTerms, SearchAdmin)
admin.site.register(AllContents, AllContentsAdmin)
 
######################################################
# all other models, this is kind of a catchall to register all models
models = apps.get_models()

for model in models:
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass
