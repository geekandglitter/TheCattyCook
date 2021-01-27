from operator import itemgetter
import sys    
from .models import AllContents

def search_func(user_terms):     
    """
    # Notes:
    1) to get an "and" condition instead of "or", just add one filter after another.
    2) But what I want is an "or" condition which I will later rank in order of number of search hits for each recipe.
    3) values() would have produced a dictionary. Instead I used values_list
    4) I couldn't used the or char with just one filter, as that would incur loss of which search terms were found
    5) So instead I am doing multiple queries, one for each search term. Thus the search terms are in a loop     
    # Known bugs: 
    1) If I type in sugar snap peas as input, it doesn't come up in bold
    2) Type in "pie" and you get too many results with "piece" or "bed" produces "cubed", "tart" leads to "start" and "starting"
    """
    num_terms = len(user_terms) # How many search terms did the user input       
    queryset=[None] * num_terms # Initialize queryset list with None    
    q_converted=[None] * num_terms # q_converted is for when we convert from list of tuples to list of lists   

    # See if the user has requested one or more ingredients to be excluded. They would do this with a minus sign.
    unwanted_ingredients = []
    for term in user_terms:
        if term[0]=="-": # If the first character is a minus sign, this means the user wants no recipes with this term in it
            unwanted_ingredients.append(term[1:]) 
            term='' # we can now remove that term from user_terms because we have set it aside in unwanted_ingredients   
     
    # Now get all the recipes that match all the remaining user search terms
    for i, term in enumerate(user_terms):
        queryset[i] = AllContents.objects.filter(fullpost__icontains=term)\
                                         .values_list('hyperlink', 'title')   # We now have a list of querysets  
    # NOTE: Change coming -- use __istartswith instead of __icontains or __iexact
    # Loop through any unwanted ingredients and exclude them    
    for neg_term in unwanted_ingredients:
        for j in range(0,num_terms):
            queryset[j] = queryset[j].exclude(fullpost__icontains=neg_term)   

    # So now we have one or more querysets (one queryset for each search term)
    # each of which each contains a list of tuples. We need to convert the list(s) of tuples to list(s) of lists.     
    for j in range(0, num_terms): # convert to a list of lists
        q_converted[j]=list(map(list, queryset[j]))     

    # Now stuff the search term(s) we found into each query result so that we can later show the user all the terms
    # satisfied by each recipe. We're putting them at position zero.
    for i, term in enumerate(user_terms): # this shows the search terms in the user's order
        for recipe in q_converted[i]:
            recipe.insert(0, term)     

    # We currently have one query result for each search term. So next, combine all the query results into one list
    combined_list=[] 
    for i in range(0,num_terms):
        combined_list = combined_list + q_converted[i] 

     

    # If the combined list is empty, then we can go ahead and return now, and tell user there are no results   
    if not combined_list:
        print("here")
        count = 0         
        trimmed_list = [['None']]
        context={'count': count, 'trimmed_list': trimmed_list}   
        return(context)      
     
    # Now sort the query results list by url so that the duplicates are grouped together   
    combined_list.sort(key=itemgetter(1))  # sort the list by the url   
   
    # This next code snippet will remove all the duplicate recipes urls, starting with some setup, and then a for loop   
    trimmed_list=[] 
    trimmed_list.append(combined_list[0]) # put the first entire recipe into trimmed_list      
    previous_recipe=trimmed_list[0]          
    recipe_counter = 1
    # Now we use a loop to remove the duplicate recipes, all the while preserving the search hits found for each recipe.
    # I designed my for loop to leverage the sortedness (done above) which grouped the duplicate recipes together
    for next_recipe in combined_list[1:]: # we need to start at the second element; that's the url
        if next_recipe[1] == previous_recipe[1]: # compare the urls
            recipe_counter += 1 # we are counting duplicates here             
            new_string = next_recipe[0] + ", " + previous_recipe[0] # We preserve the seach terms associated with each recipe                        
            trimmed_list[-1][0]= new_string # replace the search term string in the trimmed_list  
        else: # We land here when there are no more dupes in the current grouping of dupes
            # put the recipe_counter at the end of the previous record
            previous_recipe.append(str(recipe_counter))            
            recipe_counter = 1 # reset the recipe counter so we can count the next set of dupes
            trimmed_list.append(next_recipe)               
        previous_recipe = trimmed_list[-1] # now advance previous_recipe for the next time thru the loop  
    previous_recipe.append(str(recipe_counter)) # The last recipe needs its counter    
     
    for term_str in trimmed_list:     
        term_lis = term_str[0].split(',')
       
        for one_term in term_lis:       
            '''     
            if one_term[-1]=="s": 
                one_term_stripped = one_term[:-1].strip()    
            else:    
                one_term_stripped = one_term.strip()    
            '''      
            one_term_stripped = one_term.strip()          
            if (one_term_stripped.lower() in term_str[2].lower())|\
               (one_term_stripped[-1].lower() in term_str[2].lower()):
                #print(term_str[2])
                 # See if search term exists in the title
                # Make the search term bold in the title
                # What's already in the title may or may not be capitalized, so run the replace twice. 
                #if one_term_stripped[-1] == "s" and term_str[2][-1]!="s":
                 #   term_str[2] = term_str[2].replace(one_term_stripped[:-1], "<b>" + one_term_stripped.capitalize() + "</b>")
                  #  term_str[2] = term_str[2].replace(one_term_stripped[:-1].capitalize(), "<b>" + one_term_stripped.capitalize() + "</b>")
                #elif one_term_stripped[-1] != "s"and term_str[2][-1]=="s":
                 #   term_str[2] = term_str[2].replace(one_term_stripped, "<b>" + one_term_stripped.capitalize() + "</b>")
                #    term_str[2] = term_str[2].replace(one_term_stripped.capitalize(), "<b>" + one_term_stripped.capitalize() + "</b>")
                
              
                if (term_str[2][-1].lower() == "s") & (one_term_stripped[:-1].lower()== "s"):
                    term_str[2] = term_str[2].replace(one_term_stripped[:-1], "<b>" + one_term_stripped + "</b>")                 
                    term_str[2] = term_str[2].replace(one_term_stripped[:-1].capitalize(), "<b>" + one_term_stripped.capitalize() + "</b>")    
                
                elif (term_str[2][-1] == "s") & (one_term_stripped[:-1].lower() != "s"):
                    term_str[2] = term_str[2].replace(one_term_stripped, "<b>" + one_term_stripped + "</b>")                 
                    term_str[2] = term_str[2].replace(one_term_stripped.capitalize(), "<b>" + one_term_stripped.capitalize() + "</b>")    

                elif (term_str[2][-1] != "s") & (one_term_stripped[:-1].lower() != "s"):
                    term_str[2] = term_str[2].replace(one_term_stripped, "<b>" + one_term_stripped + "</b>")                 
                    term_str[2] = term_str[2].replace(one_term_stripped.capitalize(), "<b>" + one_term_stripped.capitalize() + "</b>") 

                else: 
                    term_str[2] = term_str[2].replace(one_term_stripped[:-1], "<b>" + one_term_stripped + "</b>")                 
                    term_str[2] = term_str[2].replace(one_term_stripped[:-1].capitalize(), "<b>" + one_term_stripped.capitalize() + "</b>") 
    
                 
                
    # Now get the context ready for returning to the view. Sort the results by relevancy, which is how many terms found
    count=len(trimmed_list)     
    trimmed_list.sort(key=itemgetter(-1), reverse=True) # Order and reverse the list 
    trimmed_list.sort(key=itemgetter(0)) # Sort by secondary key which will alphabetize the search terms
    trimmed_list.sort(key=itemgetter(-1), reverse=True) # Order and reverse the list 
    context={'count': count, 'trimmed_list': trimmed_list}      
    return(context)

   
 