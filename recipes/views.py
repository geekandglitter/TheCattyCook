import requests
from bs4 import BeautifulSoup
from django.shortcuts import render
from django.views.generic.list import ListView
from .models import BlogUrls
from django.http import HttpResponseRedirect
import sys
from recipes.forms import SimpleForm
from .models import AllRecipes
from operator import itemgetter
import json
import requests
import datetime as d
from requests.utils import requote_uri
import ast
from .models import BlogUrls
from .models import SearchTerms
import feedparser
from .forms import RecipeForm
import os   

 
###################################################
# VIEW
###################################################


def home(request):
    """ Shows a menu of views for the user to try """
    return render(request, 'recipes/index')


###################################################
# VIEW
###################################################
def homepagesoup(request):
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

        return render(request, 'recipes/homepagesoup',
                      {'title': title, 'mylist': anchlinklist, 'count': counter})
    except requests.ConnectionError:

        return render(request, 'recipes/error_page')


  


###################################################
# VIEW
###################################################
""" This view uses the Google Blogger API to scrape all the posts. All I needed was an API key. 
"""


def bloggerapigetalpha(request):

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

    return render(request, 'recipes/bloggerapigetalpha', {'allofit': newstring, 'count': counter})


###############################
# BLOGGERAPIGETCHRON
###############################


# Note: I had to lower the number of maxPosts above because the requests.get was throwing a server 500 error with too many posts. It
# turns out that requests is much slower than urllib.request.urlopen. This is because
# it doesn't use persistent connections: that is, it sends the header
# "Connection: close". This forces the server to close the connection immediately, so that TCP FIN comes quickly. You can reproduce
# this in Requests by sending that same header. Like this: r = requests.post(url=url, data=body, headers={'Connection':'close'})
#
# Note: I was able to improve the api call to fetchbodies = false, which speeds up the loading to some degree. Now I can allow for 200 posts
# instead of 100 posts.
def bloggerapigetchron(request):
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

    return render(request, 'recipes/bloggerapigetchron', {'allofit': newstring, 'count': counter})
 
###################################################
# ERRORS: puts up a generic error page
###################################################
def errors(request):
    return (render(request, 'recipes/error_page'))


########################################################
# Show Label List#
########################################################
def show_db_list(request):
    try:
        
        dictmap = dict()
        r = requests.get("https://thecattycook.blogspot.com")
        soup = BeautifulSoup(r.text, 'html.parser')
        somehtml = soup.find("div", {"class": "widget Label"})

        results_list = "<table><br><br>"
        for num, label in enumerate(somehtml.find_all('a'), start=0):
            if not (str(label.text[0])).isalnum():
                break  # the last label is a long blank! 
            newrec = SearchTerms.objects.update_or_create(searchterm=label.text) # add any new labels to the db  

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
        results_list = results_list + '<input type="submit" value="Send Your Choices">'

        # Now get ready to send the data to the template
        title = soup.title.text
        return render(request, 'recipes/show_db_list',
                      {'title': title, 'mylist': results_list, 'dictmap': dictmap})
    except requests.ConnectionError:
        return render(request, 'recipes/error_page')


######################################################################
# Purpose: See what boxes the user checked and display all the recipes
#
######################################################################
def db_results(request):

    getchosenlabels = request.POST.getlist('label')
    labeldict = (request.POST.getlist('dictmap'))
    newdict = ast.literal_eval(labeldict[0])
    userchoices = ""
    thelabels = "/"
    thestart = ""
    print("Here we run through all the choices")
    for choice in getchosenlabels:
        print("the choice is", choice)
        intchoice = int(choice)
        newstring = str(newdict[intchoice])
        print("newstring is", type(newstring))
        newstring = requote_uri(newstring)  # i think this is unncessary code
        print("and newstring is", type(newstring))
        # Some labels are two words such as corned beef
        userchoices = userchoices + newstring
        thelabels = thelabels + newstring + '/'
        thestart = 'https://www.blogger.com/feeds/639737653225043728/posts/default/-'
    therest = '?start-index=1&max-results=1000'
    thelink = thestart + thelabels + therest
    tempfeed1 = (feedparser.parse(thelink))
    tempfeed2 = sorted(tempfeed1.entries, key=itemgetter('title'))
    newfeed = list(tempfeed2)

    i = 0
    feed_html = ""
    for i, post in enumerate(newfeed):
        i = i + 1
        feed_html = feed_html + "<p><a href=" + \
            post.link + ">" + post.title + "</a></p>"
    return render(request, 'recipes/db_results', {'checkthem': getchosenlabels, 'getdict': feed_html, 'numposts': i})

####################################################
# Now retrieve the urls in the model using a function-based view
####################################################

def get_the_model_data(request):

    instance = BlogUrls.objects.values_list('website', flat=True).distinct()
    counter = BlogUrls.objects.values_list('numurls', flat=True).distinct()
    #return render(request, 'recipes/get_the_model_data', {'allofit': instance[0], 'counter': counter[0]})

    instance = AllRecipes.objects.values_list(
        'hyperlink', flat=True).distinct()

    allofit = ""
    for i in range(instance.count()):
        allofit = allofit+instance[i]
    return render(request, 'recipes/get_the_model_data', {'allofit': allofit, 'counter': instance.count()})


####################################################
# Now retrieve the models using class-based views (ListView) this still goes to the old BlogUrls
####################################################
class ModelList(ListView):

    model = BlogUrls  # This tells Django what model to use for the view
    # This tells Django what to name the queryset
    context_object_name = 'all_model_recipes' 

##########################################


def count_words(request):
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

    return render(request, 'recipes/count_words', {'feed_html': feed_html})
  

####################################################
# Work with models
#
###################################################


def modelfun(request):
    '''
    Uses the blogger API for Cattycook and requests to get all the posts, and stores one recipe per record in the database
   
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
            hyperlink="<a href=" + mylink['url'] + ">" +
            mylink['title'] + "</a>" + "<br>"
        )
        newrec.save()

    return render(request, 'recipes/modelfun', {'allofit': newstring, 'count': counter})

####################################################
# Model_fun_with_rss
###################################################


def modelfun_with_rss(request):
    '''
    Gets the RSS feed for Catty Cook, 150 results at a time because that is the RSS limit
    Stores one recipe per record in the database
    This is a rewrite of the original model_fun because I wanted code that uses the RSS feed. Even though
    I have to run it 150 results at a time, it's easier than using the blogger API which times out and is the
    reason why my blogger API code runs one year at a time.
    This changeover to using the RSS feed is preparation for the new view (request_input) which will search 
    for user input results
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

    return render(request, 'recipes/modelfun_with_rss', {'myfeed': feed_html, 'numposts': i})

   

#############################################
#############################################
def user_search_view(request):
    '''
    The first time this view is run, it shows a form to the user. The user is asked to input some search terms,
    separated by commas.
    The second time this view is run, it proceses the form
    Returns all recipes with any or all of the search terms. This view uses Django Models and ModelForm. I've started the code
     for storing the search terms and hyperlinks in a model for later retrieval, but this code works standalone 
     without the model code. (User can even type in a kitchen gadget or a name of someone who I might mentioned in the recipe 
     because they like it.) 
    ''' 
    # Below is some setup
    url1 = "https://thecattycook.blogspot.com/feeds/posts/default?start-index=1&max-results=150"
    url2 = "https://thecattycook.blogspot.com/feeds/posts/default?start-index=151&max-results=150"
    url3 = "https://thecattycook.blogspot.com/feeds/posts/default?start-index=301&max-results=150"
    url4 = "https://thecattycook.blogspot.com/feeds/posts/default?start-index=451&max-results=150"
    new_list = []
    final_list = []
    if request.method == 'POST': # this means the user has filled out the form
         
        form = RecipeForm(request.POST)         
         
        search_term=""
        if form.is_valid():
            cd = form.cleaned_data  # Clean the user input
            search_term = cd['user_search_terms']    
            #for oneterm in search_term: # now run through the current serach terms and save them to the database
                #newrec = SearchTerms.objects.update_or_create(searchterm=oneterm.title())                  
           
            
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
                    
                    if term.lower() in the_contents.lower() or term.lower() in the_labels.lower() or term.lower() in the_title.lower():
                                               
                        found=True
                        newrec = SearchTerms.objects.update_or_create(searchterm=term)
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
        context={'results': results, 'search_term': final_string}
        print("results is ", results)
        return render(request, 'recipes/results', context)
    else: # This code executes the first time this view is run 
        form = RecipeForm() 
    # Here is where I want to pull suggestions from a special database that has labels plus
     
    instance = SearchTerms.objects.values_list('searchterm', flat=True).distinct()
     
    words_from_database=""
    for i in range(instance.count()):
        words_from_database = words_from_database + instance[i] + "<br>"
     
    # breakdown the string into a list of words
    words = [word.lower() for word in words_from_database.split("<br>")]

    # sort the list
    words.sort() 
 
    context = {'form': form,  'words': words}    
    return render(request, 'recipes/search', context)
