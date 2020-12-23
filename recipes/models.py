# Create your models here
from django.db import models 
from django.contrib.postgres.fields import ArrayField
#from django_elastic_appsearch.orm import AppSearchModel
#from django_elastic_appsearch import serialisers

 

class AllRecipes(models.Model):
    '''
    This model holds hyperlinks (hrefs with anchor text)
    ''' 
    anchortext = models.TextField(max_length=500, null=True, blank=True)
    hyperlink = models.TextField(max_length=500, null=True, blank=True)
    extra = models.TextField(default=0)
    user_search_terms = ArrayField(models.CharField(max_length=15), null=True, blank=True)
    
    class Meta: # this eliminates the extra "s" added to the model name
        verbose_name_plural = "AllRecipes"
        ordering = ['anchortext']    # alphabetical order    
     
    def __str__(self):
        return self.hyperlink

 
class SearchTerms(models.Model):
    '''
    In the search view, the user is inputting a search term or search terms. The search term(s) will be permanently stored
    here in this model, after weeding out dupes
    ''' 
    searchterm= models.TextField(max_length=150, null=True, blank=True)

    class Meta:  # this eliminates the extra "s" added to the model name
        verbose_name_plural = "SearchTerms"
    def _str_(self):
        return self.searchterm

 


from django_elastic_appsearch.orm import AppSearchModel
from django_elastic_appsearch import serialisers

class CarSerialiser(serialisers.AppSearchSerialiser):
    full_name = serialisers.MethodField()
    make = serialisers.StrField()
    model = serialisers.StrField()
    manufactured_year = serialisers.Field()

    def get_full_name(self, instance):
        return '{} {}'.format(make, model)


class Car(AppSearchModel):

    class AppsearchMeta:
        appsearch_engine_name = 'cars'
        appsearch_serialiser_class = CarSerialiser

    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    manufactured_year = models.CharField(max_length=4)