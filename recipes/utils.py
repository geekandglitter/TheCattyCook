from operator import itemgetter
import sys    
from .models import AllContents


def search_func(user_terms): 
    print("in search function")
    num_terms = len(user_terms) 
    user_search_terms=""
    for term in user_terms:
        user_search_terms = user_search_terms + "<br>" + term

    
 
    # Note: to get an "and" condition instead of "or", just add one filter after another"
    # But I want an "or" condition which I will later rank in order of number of search hits for each recipe
    # values() would have produced a dictionary.
    # I could have used an "or" pipe character with just one filter, but then I can't easily retrieve which search hits
    # were found. So instead I am doing multiple queries, one for each search term.
    q=[None] * num_terms
    q_converted=[None] * num_terms 
    print(user_terms)    
    print("q_converted is", q_converted)
     
    for i, term in enumerate(user_terms):
        q[i] = list(AllContents.objects.filter(fullpost__icontains=term).values_list('hyperlink', 'title')) 
    for stuff in q:            
        print(stuff) 
        print("-----------")
    
    # Right here, we could have an empty queryset
  
    # So now we have q which contains num_terms number of tuples 
    for j in range(0, num_terms): # convert to a list of lists
        q_converted[j]=list(map(list, q[j]))  
    for stuff in q_converted:
        print(stuff)
        print('*********')    

    # Now stick the term(s) in each query result
    for i, term in enumerate(user_terms): # this shows the search terms in the user's order
        for recipe in q_converted[i]:
            recipe.insert(0, term)    
    for stuff in q_converted:
        print(stuff)  
        print('@@@@@@@@@@@@@@@@@@@@@@@@@@')           
    
    combined_list=[] # and finally, combine the query results into one list


    for i in range(0,num_terms):
        combined_list = combined_list + q_converted[i] 

    if not combined_list:
        count = 0
         
        trimmed_list = [['None']]
        context={'count': count, 'trimmed_list': trimmed_list, 'user_search_terms': user_search_terms}   
        return(context)      
     
    # Now sort the query results list by url so that the duplicates are grouped together   
    combined_list.sort(key=itemgetter(1))  # sort the list by the url   
    # maybe here I can sort the list by search term?
 
    trimmed_list=[]     # trimmed means the dupes will be removed, and the search hits are properly recorded for each recipe
     
    trimmed_list.append(combined_list[0]) # put the first entire recipe into trimmed_list 
     
    previous_recipe=trimmed_list[0]          
    recipe_counter = 1
    # I designed my for loop to use the sortedness (done above) which groups the duplicate recipes together
    for next_recipe in combined_list[1:]: # we need to start at the second element
        if next_recipe[1] == previous_recipe[1]: # compare the urls
            recipe_counter += 1 # we are counting duplicates here             
            new_string = next_recipe[0] + ", " + previous_recipe[0] # Might also need to alphabetize and count them 
                       
            trimmed_list[-1][0]= new_string # replace the string in the trimmed_list            
            # I think the problem is here: I need to manage those commas better
        else:
            # put the recipe_counter at the end of the previous record
            previous_recipe.append(str(recipe_counter))  
          
            recipe_counter = 1 # reset the recipe counter because we are in the else
            trimmed_list.append(next_recipe)               
        previous_recipe = trimmed_list[-1] # now advance previous_recipe for the next time thru the loop  
    previous_recipe.append(str(recipe_counter)) # The last recipe needs its counter 
    print("prev recipe is", previous_recipe)
    for stuff in previous_recipe:
        print("STUFF")
        print (stuff)
     
    # Now get the context ready for the template   
    
    count=len(trimmed_list)  
    
    
    trimmed_list.sort(key=itemgetter(-1), reverse=True) # then, sort by primary key which will order the list by how many search terms were found for each recipe. We reverse this seond sort for relevance ranking
     
    trimmed_list.sort(key=itemgetter(0)) # sort by secondary key which will alphabetize the search terms
    
    trimmed_list.sort(key=itemgetter(-1), reverse=True) # then, sort by primary key which will order the list by how many search terms were found for each recipe. We reverse this seond sort for relevance ranking
     
    context={'count': count, 'trimmed_list': trimmed_list, 'user_search_terms': user_search_terms}     
     

    return(context)