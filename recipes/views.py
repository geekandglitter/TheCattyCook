import requests
from bs4 import BeautifulSoup
from django.shortcuts import render
from django.views.generic.list import ListView
 
from django.http import HttpResponseRedirect
import sys
#from recipes.forms import SimpleForm
from .models import AllRecipes
from operator import itemgetter
import json
import requests
import datetime as d
from requests.utils import requote_uri
import ast

from .models import SearchTerms
import feedparser
from .forms import RecipeForm
import os   


from .models import AllContents
 

 
###################################################
# VIEW
###################################################


def home(request):
    """ Shows a menu of views for the user to try """
    return render(request, 'recipes/index')


###################################################
# Uses beautifulsoup, only to scrape the homepage
###################################################
def scrape_view(request):
    """ Demonstrates scraping posts from the home page"""
    try:
        r = requests.get("https://thecattycook.blogspot.com")
        soup = BeautifulSoup(r.text, 'html.parser')

        anchor_links = sorted(soup.find_all('a'), key=lambda elem: elem.text)
        counter = 0
        anchlinklist = ""  # will build a list of anchor text
        title = soup.title.text
        for anchlink in anchor_links:

            if anchlink.parent.name == 'h3':
                counter += 1
                anchlinklist = anchlinklist + str(anchlink) + "<br>"

        return render(request, 'recipes/scrape',
                      {'title': title, 'mylist': anchlinklist, 'count': counter})
    except requests.ConnectionError:

        return render(request, 'recipes/error_page')


  


###################################################
# This view GETS the posts using Google Blogger API and "request.get"
###################################################
""" This view uses the Google Blogger API to retreive all the posts. All I needed was an API key. 
"""


def get_view(request):

    def request_by_year(edate, sdate):

        # Initially I did the entire request at once, but I had to chunk it into years because it was timing out in
        # windows.

        url_part_1 = "https://www.googleapis.com/blogger/v3/blogs/639737653225043728/posts?endDate="
        url_part_2 = edate + "&fetchBodies=false&maxResults=500&startDate=" + sdate
        url_part_3 = "&status=live&view=READER&fields=items(title%2Curl)&key=AIzaSyDleLQNXOzdCSTGhu5p6CPyBm92we3balg"
        url = url_part_1 + url_part_2 + url_part_3

        r = requests.get(url, stream=True)
        q = json.loads(r.text)  # this is the better way to unstring it
        if not q:
            s = []
        else:
            s = q['items']

        return s

    accum_list = []

    c_year = int(d.datetime.now().year)

    for the_year in range(2014, c_year + 1):
        enddate = str(the_year) + "-12-31T00%3A00%3A00-00%3A00"
        startdate = str(the_year) + "-01-01T00%3A00%3A00-00%3A00"

        t = request_by_year(enddate, startdate)
        accum_list = accum_list + t

    sorteditems = sorted(accum_list, key=itemgetter('title'), reverse=True)
    counter = 0
    newstring = " "
    for mylink in sorteditems:
        counter += 1
        newstring = "<a href=" + mylink['url'] + ">" + \
            mylink['title'] + "</a>" + "<br>" + newstring

    return render(request, 'recipes/get', {'allofit': newstring, 'count': counter}) 

###############################
# This view does the same as get_view but orders the results by date instead of alphabetically
###############################

# Note: I had to lower the number of maxPosts above because the requests.get was throwing a server 500 error with too many posts. It
# turns out that requests is much slower than urllib.request.urlopen. This is because
# it doesn't use persistent connections: that is, it sends the header
# "Connection: close". This forces the server to close the connection immediately, so that TCP FIN comes quickly. You can reproduce
# this in Requests by sending that same header. Like this: r = requests.post(url=url, data=body, headers={'Connection':'close'})
#
# Note: I was able to improve the api call to fetchbodies = false, which speeds up the loading to some degree. Now I can allow for 200 posts
# instead of 100 posts.
def getchron_view(request):
    def request_by_year(edate, sdate):
        # Initially I did the entire request at once, but I had to chunk it into years because it was timing out in windows.

        url = "https://www.googleapis.com/blogger/v3/blogs/639737653225043728/posts?endDate=" + edate + "&fetchBodies=false&maxResults=500&startDate=" + \
            sdate + \
            "&status=live&view=READER&fields=items(title%2Curl)&key=AIzaSyDleLQNXOzdCSTGhu5p6CPyBm92we3balg"
        r = requests.get(url, stream=True)
        q = json.loads(r.text)  # this is the better way to unstring it
        if not q:
            s = []
        else:
            s = q['items']
        return (s)

    accum_list = []

    c_year = int(d.datetime.now().year)
    for the_year in range(2014, c_year + 1):
        enddate = str(the_year) + "-12-31T00%3A00%3A00-00%3A00"
        startdate = str(the_year) + "-01-01T00%3A00%3A00-00%3A00"
        t = request_by_year(enddate, startdate)
        accum_list = t + accum_list

    counter = 0
    newstring = " "
    for mylink in accum_list:
        counter += 1
        newstring = "<a href=" + mylink['url'] + ">" + \
            mylink['title'] + "</a>" + "<br>" + newstring

    return render(request, 'recipes/getchron', {'allofit': newstring, 'count': counter})
 
###################################################
# ERRORS: puts up a generic error page. Maybe I have to turn off debug to see this? I don't know.
###################################################
def errors_view(request):
    return (render(request, 'recipes/error_page'))

######################################################################
# Purpose: See what boxes the user checked and display all the recipes
######################################################################
def searchboxes_view(request):
    
    search_term = request.POST.getlist('label') # should change its name to user_choices 
    labeldict = (request.POST.getlist('dictmap'))
    newdict = ast.literal_eval(labeldict[0])
 
    # what I need to do here is translate the numbers into the names
    new_search_term=[]
    for key in newdict.keys():
        if str(key) in search_term:
             
            new_search_term.append(newdict[key])
    
    search_term=new_search_term
    url1 = "https://thecattycook.blogspot.com/feeds/posts/default?start-index=1&max-results=150"
    url2 = "https://thecattycook.blogspot.com/feeds/posts/default?start-index=151&max-results=150"
    url3 = "https://thecattycook.blogspot.com/feeds/posts/default?start-index=301&max-results=150"
    url4 = "https://thecattycook.blogspot.com/feeds/posts/default?start-index=451&max-results=150"
    feed1 = (feedparser.parse(url1))                
    feed2 = (feedparser.parse(url2))
    feed3 = (feedparser.parse(url3))
    feed4 = (feedparser.parse(url4))    
    newfeed1 = list(feed1.entries)
    newfeed2 = list(feed2.entries)
    newfeed3 = list(feed3.entries)
    newfeed4 = list(feed4.entries)
    newfeed = newfeed1 + newfeed2 + newfeed3 + newfeed4  
 
    final_list = []       
    count=0
    for eachrecipe in newfeed: # Now check each recipe for the user's search terms
              
        r = requests.get(eachrecipe.link)
        soup = BeautifulSoup(r.text, 'html.parser')                
        the_labels = str(soup.find("span", class_="post-labels"))                
        the_title = eachrecipe.title       
        the_contents = str(soup.find("div", class_="post-body entry-content"))   
                
        temp_list=[]
        found=False
        num_terms_found = 0
        search_term_string=""
        for term in search_term:   
                    
            if term.lower() in the_contents.lower() or term.lower() in the_labels.lower() or term.lower() in the_title.lower():
                                               
                found=True
                
                newrec = SearchTerms.objects.update_or_create(searchterm=term.lower())
                num_terms_found+=1
                search_term_string = search_term_string + " " + term    
                 
                thelink = ["(" + 
                               str(num_terms_found) + 
                                ")" +
                                
                                " " +
                                "<a href=" + eachrecipe.link + 
                                ">" + 
                                "<b>" +
                                eachrecipe.title +
                                "</b>" + "</a>" + 
                                " " +
                                "<br>" +
                                search_term_string +
                                "<br><br>"]
                if found:
                    temp_list = thelink       
                else:
                    # QUESTION: Is this else ever happening?
                    temp_list.append(thelink)
        # Here manage the dupes in temp_list before adding it to final_list
        if found:
            count+=1
        final_list.extend(temp_list)     
        #if not final_list:
         #   final_list.append("<b>none</b>")
             
        results = sorted(final_list, reverse=True)
        final_string=""
        for eachstring in search_term:
            final_string += eachstring + " "
        context={'count': count, 'results': results, 'search_term': final_string}         

    #return render(request, 'recipes/db_results', {'checkthem': search_term, 'numposts': i})
 
    return render(request, 'recipes/suggestionresults', context) 

####################################################
# Now retrieve the urls from the model using a function-based view, and renders them
####################################################

def retrieve_recipes_view(request):
     
    instance = AllRecipes.objects.values_list(
        'hyperlink', flat=True).distinct()
    allofit = ""
    for i in range(instance.count()):
        allofit = allofit+instance[i]
    return render(request, 'recipes/retrieve-recipes', {'allofit': allofit, 'counter': instance.count()})

#################################################################################
# CLASS BASED VIEW Now retrieve the models using class-based views (ListView) 
#################################################################################
class ModelList(ListView): # ListView doesn't have a template

    model = AllRecipes  # This tells Django which model to create listview for
    # I left all the defaults.
    # The default name of the queryset is object_list. It can be changed like this: context_object_name='all_model_recipes' 
    # The default template becomes allrecipes_list.html
 
##########################################
def count_words_view(request):
    '''
    # get the recipes from the RSS feed
    # loop through each recipe and count its words.
    # If word count is less than a hundred, store the recipe in a dictionary
    # create a list of all the dictionaries
    '''

    feed = (feedparser.parse(
        'https://thecattycook.blogspot.com/feeds/posts/default?start-index=1&max-results=1000'))
    feed_html = ""
    newfeed = list(feed.entries)

    for i, post in enumerate(newfeed):
        i = i + 1
        r = requests.get(post.link)
        soup = BeautifulSoup(r.text, 'html.parser')
        r = requests.get(post.link)
        soup = BeautifulSoup(r.text, 'html.parser')
        result = soup.find(itemprop='description articleBody')

        the_length = len(result.get_text())
        if the_length < 300:
            if post.title == "":
               post.title = "NO TITLE"
            feed_html = feed_html + "<a href=" + post.link + ">" + \
                post.title + "</a>" + " " + str(the_length) + "<br>"

    if not feed_html:
        feed_html = "none"

    return render(request, 'recipes/count-words', {'feed_html': feed_html})
  

####################################################
# This view uses the blogger API to get all the posts and stores them in the db
###################################################

def get_and_store_view(request):
    '''
    Uses the blogger API and the requests module to get all the posts, and stores one recipe per record in the database   
    '''
    def request_by_year(edate, sdate):
        # Initially I did the entire request at once, but I had to chunk it into years because it was timing out in windows.

        url = "https://www.googleapis.com/blogger/v3/blogs/639737653225043728/posts?endDate=" + edate + "&fetchBodies=false&maxResults=500&startDate=" + \
            sdate + \
            "&status=live&view=READER&fields=items(title%2Curl)&key=AIzaSyDleLQNXOzdCSTGhu5p6CPyBm92we3balg"

        r = requests.get(url, stream=True)
        q = json.loads(r.text)  # this is the better way to unstring it
        if not q:
            s = []
        else:
            s = q['items']
        return (s)

    accum_list = []  # this will become a list of dictionaries
    c_year = int(d.datetime.now().year)

    for the_year in range(2014, c_year + 1):
        enddate = str(the_year) + "-12-31T00%3A00%3A00-00%3A00"
        startdate = str(the_year) + "-01-01T00%3A00%3A00-00%3A00"
        t = request_by_year(enddate, startdate)
        accum_list = accum_list + t

    sorteditems = sorted(accum_list, key=itemgetter('title'), reverse=True)
    counter = 0
    newstring = " "
    # Now we get ready to update the database
    AllRecipes.objects.all().delete()  # clear the table
    for mylink in sorteditems:
         
        counter += 1
        newstring = "<a href=" + mylink['url'] + ">" + \
            mylink['title'] + "</a>" + "<br>" + newstring
            # Below, notice I stuff the title in with the body. It makes the title search part of the contents search.
        newrec = AllRecipes.objects.create(
            anchortext=mylink['title'],
            hyperlink="<a href=" + mylink['url'] + ">" + mylink['title'] + "</a>" + "<br>",
            url=mylink['url']
        )
        newrec.save()

    return render(request, 'recipes/get-and-store', {'allofit': newstring, 'count': counter})

####################################################
# FEEDPARSE_VIEW
###################################################


def feedparse_view(request):
    '''
    Gets the RSS feed for Catty Cook, 150 results at a time because that is the RSS limit
    Stores one recipe per record in the database
    This is a rewrite of the original model_fun because I wanted code that uses the RSS feed. Even though
    I have to run it 150 results at a time, it's easier than using the blogger API which times out and is the
    reason why my blogger API code runs one year at a time.
     
    '''
    global i

    feed1 = (feedparser.parse(
        "https://thecattycook.blogspot.com/feeds/posts/default?start-index=1&max-results=150"	))
    newfeed1 = list(feed1.entries)
    feed2 = (feedparser.parse(
        "https://thecattycook.blogspot.com/feeds/posts/default?start-index=151&max-results=150"))
    newfeed2 = list(feed2.entries)
    feed3 = (feedparser.parse(
        "https://thecattycook.blogspot.com/feeds/posts/default?start-index=301&max-results=150"))
    newfeed3 = list(feed3.entries)

    feed_html = ""
    # these three loops are only for putting the hyperlinks out to the page
    for i, post in enumerate(newfeed1+newfeed2+newfeed3):
        i = i + 1
        feed_html = feed_html + "<a href=" + post.link + ">" + post.title + "</a><br>"

    # Now before we go rendering results in html, we also want to update the database
    counter = 0
    newstring = " "
    # Now we get ready to update the database
    AllRecipes.objects.all().delete()  # clear the table
    for mylink in newfeed1 + newfeed2 + newfeed3:
        counter += 1
        newstring = "<a href=" + mylink['link'] + ">" + \
            mylink['title'] + "</a>" + "<br>" + newstring
        newrec = AllRecipes.objects.create(
            anchortext=mylink['title'],
            hyperlink="<a href=" + mylink['link'] +
            ">" + mylink['title'] + "</a>" + "<br>"
        )
        newrec.save()

    return render(request, 'recipes/feedparse', {'myfeed': feed_html, 'numposts': i})

   

#############################################
#############################################
def searchinput_view(request):
    '''
    The first time this view is run, it shows a text input box to the user. The user is asked to input some search terms,
    separated by commas.
    The second time this view is run, it processes the form.
    It returns all recipes with any or all of the search terms.  
    It also updates the database with all the valid search terms (terms which had been found)
     
    ''' 
    # Below is some setup
    url1 = "https://thecattycook.blogspot.com/feeds/posts/default?start-index=1&max-results=150"
    url2 = "https://thecattycook.blogspot.com/feeds/posts/default?start-index=151&max-results=150"
    url3 = "https://thecattycook.blogspot.com/feeds/posts/default?start-index=301&max-results=150"
    url4 = "https://thecattycook.blogspot.com/feeds/posts/default?start-index=451&max-results=150"
  
    final_list = []
    count = 0
    form = RecipeForm(request.POST)       
    if request.method == 'POST': # this means the user has filled out the form  
              
        user_terms=""
        if form.is_valid():
            
            cd = form.cleaned_data  # Clean the user input
            user_terms = cd['user_search_terms']     
             
             
            # Note about code below: Blogger limits RSS feeds to 150
            # So I get the lists and put them together     
            feed1 = (feedparser.parse(url1))                
            feed2 = (feedparser.parse(url2))
            feed3 = (feedparser.parse(url3))
            feed4 = (feedparser.parse(url4))
            newfeed1 = list(feed1.entries)
            newfeed2 = list(feed2.entries)
            newfeed3 = list(feed3.entries)
            newfeed4 = list(feed4.entries)
            newfeed = newfeed1 + newfeed2 + newfeed3 + newfeed4           

            for eachrecipe in newfeed: # Now check each recipe for the user's search terms
              
                r = requests.get(eachrecipe.link)
                soup = BeautifulSoup(r.text, 'html.parser')                
                the_labels = str(soup.find("span", class_="post-labels"))                
                the_title = eachrecipe.title       
                the_contents = str(soup.find("div", class_="post-body entry-content"))   
                
                temp_list=[]
                found=False
                num_terms_found = 0
                search_term_string=""
                for term in user_terms:   
                    # if the search terms(s) are found, add them to the search term database
                    if term.lower() in the_contents.lower() or term.lower() in the_labels.lower() or term.lower() in the_title.lower():
                        #count += 1                       
                        found=True
                        newrec = SearchTerms.objects.update_or_create(searchterm=term.lower())
                        num_terms_found+=1
                        search_term_string = search_term_string + " " + term    
                        thelink = ["(" + 
                                  str(num_terms_found) + 
                                  ")" +
                                  " " +
                                  "<a href=" + eachrecipe.link + 
                                  ">" + 
                                  "<b>" +
                                  eachrecipe.title +
                                  "</b>" + "</a>" + 
                                  " " +
                                  "<br>" +
                                  search_term_string +
                                  "<br><br>"] 
                        
                        if found:
                            temp_list = thelink       
                        else:
                            # QUESTION: Is this else ever happening?
                            temp_list.append(thelink)
                # Here manage the dupes in temp_list before adding it to final_list
                if found:
                    count +=1
                final_list.extend(temp_list)     
        if not final_list:
            final_list.append("<b>none</b>")
             
        results = sorted(final_list, reverse=True)
        final_string=""
        for eachstring in user_terms:
            final_string += eachstring + " "
        final_string = "<br>" + "Showing " + str(count) + " results for: " + final_string    
        context={'count': count, 'results': results, 'user_terms': final_string, 'form': form}
         
     
    else: # This code executes the first time this view is run        
        context = {'form': form}    
   
     
    return render(request, 'recipes/searchinput', context)


########################################################
# Show Label List plus all other search terms that have been stored by the user
########################################################
def suggestions_view(request):
    def update_the_database_with_labels(soup):        
        somehtml = soup.find("div", {"class": "widget Label"})      
        for num, label in enumerate(somehtml.find_all('a'), start=0):
            if not (str(label.text[0])).isalnum():
                break  # the last label is a long blank! 
            newrec = SearchTerms.objects.update_or_create(searchterm=label.text.lower()) # add any new labels to the db  
        return(soup)    
    try:
        results_list = "<table><br><br>"
        results_list = results_list + '<input type="submit" value="Search"><br><br>'  
        r = requests.get("https://thecattycook.blogspot.com")
        soup = BeautifulSoup(r.text, 'html.parser')
        update_the_database_with_labels(soup) # this line can be turned off
        dictmap = dict()       

        # Next we want to fetch whatever is in the database. Those items will become the checkboxes
        instance = SearchTerms.objects.values_list(
            'searchterm', flat=True).distinct().order_by('searchterm')  # alphabetize this queryset

        for mynum, search_term_in_db in enumerate(instance, start=1): 
            results_list = results_list + \
                 "<td>" '''<input type="checkbox" name="label" value=''' + \
                 str(mynum) + ">" + \
                 str(search_term_in_db) + \
                 "    " + \
                 "</td>"

            if mynum % 4 == 0 and mynum != 0:  # this modulo is for formatting on the screen
                results_list = results_list + "</tr><tr>"
            dictmap[mynum] = str(search_term_in_db)  
         
        results_list = results_list + "</table>"
        results_list = results_list + \
            '<br>' '''<input type="hidden" name="dictmap" value=''' + \
            str(dictmap) + ">"
        results_list = results_list + '<input type="submit" value="Search">'

        # Now get ready to send the data to the template
        title = soup.title.text
        return render(request, 'recipes/suggestions',
                      {'title': title, 'mylist': results_list, 'dictmap': dictmap})
    except requests.ConnectionError:
        return render(request, 'recipes/error_page')
 

#############
def scrapecontents_view(request):
    '''
    Scrape the contents of every recipe post
    Here's the psuedocode:
    1. X Go into the allrecipes model
    2. X Retrieve all the hyperlinks and put them in a list
    3. X Loop through the hyperlinks
        a. X Get post and find everything inside post-body, eliminate all html
        b. X Store all contents in the new model AllContents.Fullpost    
        c. X Also update AllCOntents.Hyperlink        
    4. X Put something out to the template 
 
    '''
    # First, get all the urls from AllRecipes
    instance = AllRecipes.objects.filter().values_list('url', 'anchortext')

    # For now, I'm starting over each time, by emptying out AllContents
    AllContents.objects.all().delete()  # clear the table 
    for hyper, title in instance:
         
         
        getpost = requests.get(hyper)
        soup = BeautifulSoup(getpost.text, 'html.parser')            
        soup_contents = soup.find("div", class_="post-body entry-content") 
        stripped = title + soup_contents.get_text()
     
        stripped = ' '.join(stripped.split()) # remove all multiple blanks, leave single blanks
       
         
         
        newrec = AllContents.objects.create(
            fullpost=stripped,       
            hyperlink=hyper,
            title=title

        )
        newrec.save()
             
    return render(request, 'recipes/scrapecontents')

 
def modelsearch_view(request):
    '''
    I found out how to loop through all the search terms from the brilliant guy who
    answered it in stackoverflow:
    https://stackoverflow.com/questions/43549479/how-to-search-for-multiple-keywords-over-multiple-columns-in-django
    Also:
    https://stackoverflow.com/questions/43549479/how-to-search-for-multiple-keywords-over-multiple-columns-in-django
    https://docs.djangoproject.com/en/3.1/ref/models/conditional-expressions/
    https://bradmontgomery.net/blog/adding-q-objects-in-django/
    https://riptutorial.com/django/example/4565/advanced-queries-with-q-objects    
    Case(When(q_object.add((Q(fullpost__icontains=item)| \
                      Q(title__icontains=item)), q_object.connector) ))
    '''
    from operator import itemgetter
    term1 = "soy sauce"
    term2 = "shrimp" 
    term3 = "stir fry"
    user_search_terms = "<br>" + term1 + "<br>" + term2 + "<br>" + term3
    # Note: to get an "and" condition instead of "or", just add one filter after another
  
    q1 = list(AllContents.objects.filter(fullpost__icontains=term1).values_list())    
    q2 = list(AllContents.objects.filter(fullpost__icontains=term2).values_list())
    q3 = list(AllContents.objects.filter(fullpost__icontains=term3).values_list())
    # Next, convert each list of tuples into a list of lists
    q1_converted = list(map(list, q1)) 
    q2_converted = list(map(list, q2)) 
    q3_converted = list(map(list, q3)) 
 
    for recipe in q1_converted:
        recipe.insert(0, term1)  
    for recipe in q2_converted:
        recipe.insert(0, term2)
    for recipe in q3_converted:
        recipe.insert(0, term3)        
    full_list = q1_converted + q2_converted + q3_converted    
    # Now sort by id or url so that the duplicates are grouped together   
    new_list=sorted(full_list, key=itemgetter(2))  # sort the list by the url (or could have used the id)
    #print(new_list[0]) 
    trimmed_list=[] 
   
    
    trimmed_list.append(new_list[0]) # put the first entire recipe into trimmed_list    
    previous_record=trimmed_list[0]     
    # in the for loop, I use the sortedness (done above) which groups the duplicate recipes together
    recipe_counter = 1
    for next_recipe in new_list[1:]: # we need to start at the second element
        if next_recipe[2] == previous_record[2]:
            recipe_counter += 1 
            #print("found a dupe")
            #print("search term in next recipe is", next_recipe[0]) 
            #print("search term already in trimmed list is", previous_record[0])
            new_string = next_recipe[0] + ", " + previous_record[0] # Might also need to alphabetize and count them
            #print("new string is", new_string)
            trimmed_list[-1][0]= new_string
            # then replace the string only in the new list
            print("recipe counter is",  recipe_counter)
        else:
            # put the recipe_counter at the end of next_recipe
            previous_record.append(', ' + str(recipe_counter)) 
            recipe_counter = 1 # reset the recipe counter
            trimmed_list.append(next_recipe)  
            #print("appended ")
        previous_record = trimmed_list[-1] 
    
    for this in trimmed_list:
        print(this[0]) # search terms
        print(this[1]) # id
        print(this[2]) # url
        print(this[3]) # title
        #print(this[4]) # recipe contents   

    count=len(trimmed_list)    
    almost_final_list=sorted(trimmed_list, key=itemgetter(0)) # sort by secondary key which will alphabetize the search terms
    final_list=sorted(almost_final_list, key=itemgetter(-1), reverse=True) # then, sort by primary key which will order the list by how many search terms were found for each recipe. We reverse this seond sort for relevance ranking
    context={'count': count, 'final_list': final_list, 'user_search_terms': user_search_terms}    
    return render(request, 'recipes/modelsearch', context)    
 