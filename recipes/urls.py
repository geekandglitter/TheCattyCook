""" URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from django.contrib import admin
from recipes import views
from django.urls import path
from .views import ModelList # this is for the new class-based view

#The new django.urls.path() function allows a simpler, more readable URL routing syntax.
from recipes.models import AllRecipes

urlpatterns = [
 
  path("admin/", admin.site.urls),  # Activates the admin interface 
  path('', views.home, name='home'),   
  path('error_page', views.errors),
  path('scraped', views.scrape_view),   
  path('gotten', views.get_view),
  path('gottenchron', views.getchron_view), 
  path('searchsuggestions', views.searchsuggestions),
  path('searchresults', views.searchinput),  
  path('get-the-model-data', views.get_the_model_data),
  path('go-here', ModelList.as_view(model=AllRecipes)), 
  path('count-words', views.count_words_view),   
  path('modelfun', views.modelfun),
  path('feedparsed', views.feedparse_view), 
  path('searchedinput', views.searchinput_view),
  

  
]

 
