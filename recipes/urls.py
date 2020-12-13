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
from recipes.models import BlogUrls

urlpatterns = [
  #url(r'^admin/', admin.site.urls),
  path("admin/", admin.site.urls),  # Activates the admin interface
  url(r'^$', views.home, name='home'),
  url('error_page', views.errors),
  url('homepagesoup', views.homepagesoup),
  #url('getfeedalpha', views.getfeedalpha),
  #path('getfeedchron', views.getfeedchron),
  url('bloggerapigetalpha', views.bloggerapigetalpha),
  url('bloggerapigetchron', views.bloggerapigetchron),
 
  path('searchsuggestions', views.searchsuggestions),
  path('db_results', views.db_results),  
  path('get-the-model-data', views.get_the_model_data),
  path('BlogUrls_list', ModelList.as_view(model=BlogUrls)), 
  path('count_words', views.count_words),   
  path('modelfun', views.modelfun),
  path('modelfun_with_rss', views.modelfun_with_rss), 
  path('search', views.user_search_view),
  

  
]





