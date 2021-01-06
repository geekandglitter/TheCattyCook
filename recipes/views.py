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
from googleapiclient.discovery import build

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
                count+=1
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
         
              
        search_term=""
        if form.is_valid():
            
            cd = form.cleaned_data  # Clean the user input
            search_term = cd['user_search_terms']     
             
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
                for term in search_term:   
                    # if the search terms(s) are found, add them to the search term database
                    if term.lower() in the_contents.lower() or term.lower() in the_labels.lower() or term.lower() in the_title.lower():
                        count += 1                       
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
                final_list.extend(temp_list)     
        if not final_list:
            final_list.append("<b>none</b>")
             
        results = sorted(final_list, reverse=True)
        final_string=""
        for eachstring in search_term:
            final_string += eachstring + " "
        final_string = "<br>" + "Showing " + str(count) + " results for: " + final_string    
        context={'count': count, 'results': results, 'search_term': final_string, 'form': form}
         
     
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
def allcontents_view(request):
    '''
    I figured this out with the help of a youtube video about google blogger API with Python.   
    https://youtu.be/6nAnSi0yAM8
    Or go into youbute and look for this: shah google blogger api #1
    NOT IN USE. I'M GIVING UP ON THIS VIEW
    '''
    Key="AIzaSyDleLQNXOzdCSTGhu5p6CPyBm92we3balg"
    BlogId="639737653225043728"
    blog=build('blogger', 'v3', developerKey=Key)
    print("blog is", blog)
         
    #r = requests.get(url, stream=True)
    resp = blog.blogs().get(blogId=BlogId).execute()
    #print("resp is", resp)
     
    print(resp['name'])
    print(resp.get("name"))
    print(resp['updated'])
    print(resp['posts'])
    print(resp['posts']['totalItems'])
    numitems = resp['posts']['totalItems']
    print(resp['posts']['selfLink'])



    resp = blog.posts().list(blogId=BlogId).execute()
    
    print("now resp is", resp)
    print("And here we go")
    #print(resp)
    out_to_screen = resp["items"][0]["content"]
    print("Zero:")
    #print(resp["items"][0]["content"])
    print("One:")
    #print(resp["items"][1]["content"])
    print("Two:")
    #print(resp["items"][2]["content"])
    print(resp["items"][2]["url"])
    """
    for i in range(0,11):
        print("Number", i)
        print(resp["items"][i]["content"])
        print("*********************************************")
    """    
    print("numitems is", numitems)       
         
    return render(request, 'recipes/allcontents')
#############
def scrapecontents_view(request):
    '''
    1. Go into the allrecipes model
    2. Retrieve all the hyperlinks and put them in a list
    3. Loop through the hyperlinks
        a. Get post and find everything inside post-body, eliminate all html
        b. Store all contents in the new model AllContents.Fullpost
        c. Also update AllContents.Anchortext
        d. Also update AllCOntents.Hyperlink
        e. Also update AllContents.Title
    4. Put something out to the template 
    '''
    #instance = AllRecipes.objects.all().values_list('hyperlink')
     

    instance = AllRecipes.objects.filter().values_list('url', flat=True)
    #print(instance)
    for hyper in instance:
        #print(hyper,"\n")
        getpost = requests.get(hyper)
        soup = BeautifulSoup(getpost.text, 'html.parser')
        # Examples of what we're looking for:
        # <div class='post-body entry-content' id='post-body-5858122903732271900' itemprop='description articleBody'>
        # <div class='post-body entry-content' id='post-body-6450619777393005693' itemprop='description articleBody'>        
        soup_contents = soup.find("div", class_="post-body entry-content") 
        stripped = soup_contents.get_text()
        stripped = ' '.join(stripped.split())
        print(stripped)
             
    return render(request, 'recipes/scrapecontents')
 