from operator import itemgetter
import sys    
from .models import AllContents


def search_func(user_terms):
    
    user_terms = ("bread", "butter", "milk")
    #print(user_terms[0])
    #print(user_terms[1])
    #print(user_terms[2])
     
    #for term in user_terms:
        #print (term)

    #print(len(user_terms))   
    num_terms = len(user_terms) 
 
    # Note: to get an "and" condition instead of "or", just add one filter after another"
    # But I want an "or" condition which I will later rank in order of number of search hits for each recipe
    # values() would have produced a dictionary.
    # I could have used an "or" pipe character with just one filter, but then I can't easily retrieve which search hits
    # were found. So instead I am doing multiple queries, one for each search term.
    q=[None] * num_terms
    q_converted=[None] * num_terms
     
    i=0 
    for i, term in enumerate(user_terms):
        q[i] = list(AllContents.objects.filter(fullpost__icontains=term).values_list('hyperlink', 'title'))  
        i += 1
     
     

    # So now we have q which contains num_terms number of tuples 
    for j in range(0, num_terms): # convert to a list of lists
        q_converted[j]=list(map(list, q[j]))

    

    
 
 
    i = 0 
    # Now stick the term in each query result
    for i, term in enumerate(user_terms):
        for recipe in q_converted[i]:
            recipe.insert(0, term)  
       
        i+=1



    combined_list=[]
    for i in range(0,num_terms):
        combined_list = combined_list + q_converted[i]

     

    # Now sort by  url so that the duplicates are grouped together   
    combined_list.sort(key=itemgetter(1))  # sort the list by the url   
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
        else:
            # put the recipe_counter at the end of the previous record
            previous_recipe.append(', ' + str(recipe_counter)) # this sometimes produces empty commas
            recipe_counter = 1 # reset the recipe counter because we are in the else
            trimmed_list.append(next_recipe)               
        previous_recipe = trimmed_list[-1] # now advance previous_recipe for the next time thru the loop
         
     
    previous_recipe.append(', ' + str(recipe_counter)) # The last recipe needs its counter
    
 
    # Now get ready for the template
    
    user_search_terms=""
    for term in user_terms:
        user_search_terms = user_search_terms + "<br>" + term

    count=len(trimmed_list)  
    trimmed_list.sort(key=itemgetter(0)) # sort by secondary key which will alphabetize the search terms
    trimmed_list.sort(key=itemgetter(-1), reverse=True) # then, sort by primary key which will order the list by how many search terms were found for each recipe. We reverse this seond sort for relevance ranking
    context={'count': count, 'trimmed_list': trimmed_list, 'user_search_terms': user_search_terms} 
     
     
    return(context)