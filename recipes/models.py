# Create your models here
from django.db import models
 
from django.contrib.postgres.fields import ArrayField


#class Person(models.Model):
  #  first_name = models.CharField(max_length=30)
  #  last_name = models.CharField(max_length=30)
  #  def __str__(self):
  #     return self.first_name, self.last_name

class BlogUrls(models.Model):
    '''
    This model holds hyperlinks (hrefs with anchor text)
    '''
    website=models.TextField(max_length=9000)
    numurls=models.IntegerField(0)

    class Meta:  # this eliminates the extra "s" added to the model namez
        verbose_name_plural = "BlogUrls"
    def __str__(self):
        return self.website


class AllRecipes(models.Model):
    '''
    This model holds hyperlinks (hrefs with anchor text)
    '''
     
    #readonly_fields = ('id',)
    anchortext = models.TextField(max_length=500, null=True, blank=True)
    hyperlink = models.TextField(max_length=500, null=True, blank=True)
    extra = models.TextField(default=0)
    user_search_terms = ArrayField(models.CharField(max_length=15), null=True, blank=True)
    #moretags = ArrayField(models.CharField(max_length=15), null=True, blank=True)
    #mypk = models.AutoField(primary_key=True)
    #primary_key = True

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
    
    searchterm= models.TextField(max_length=50, null=True, blank=True)

    class Meta:  # this eliminates the extra "s" added to the model name
        verbose_name_plural = "SearchTerms"
    def _str_(self):
        return self.searchterm
