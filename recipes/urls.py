 
from django.contrib import admin
from django.urls import path 
from recipes import views 
from .views import ModelList # this is for the new class-based view
from recipes.models import AllRecipes

urlpatterns = [
 
  path("admin/", admin.site.urls),  # Activates the admin interface 
  path('', views.home, name='home'),  
   
  path('error', views.errors_view),
  path('scrape', views.scrape_view),   
  path('get', views.get_view),
  path('getchron', views.getchron_view), 
  path('suggestions', views.suggestions_view),
  path('suggestionresults', views.searchboxes_view),  
  path('retrieve-recipes', views.retrieve_recipes_view),
  path('retrieve-recipes-classbased', ModelList.as_view(model=AllRecipes)), 
  path('count-words', views.count_words_view),   
  path('get-and-store', views.get_and_store_view),
  path('feedparse', views.feedparse_view), 
  path('searchinput', views.searchinput_view),    # No longer in use
  path('scrapecontents', views.scrapecontents_view),
  path('modelsearch', views.modelsearch_view),
  
]

 
