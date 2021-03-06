from pymongo import MongoClient
import urllib2

def connect():
	client = MongoClient()
	return client

def set_up(client):
	# db = client.db
	# db.recipe.drop()
	# recipe_collection = db.recipe
	# recipe_collection.insert({"recipe_name":"R1", "ingredient":"I1", "weight":1, "req":True, "rating": 100, "url":"www.google.com"})
	# recipe_collection.insert({"recipe_name":"R1", "ingredient":"I2", "weight":2, "req":False, "rating": 100, "url":"www.google.com"})
	# recipe_collection.insert({"recipe_name":"R2", "ingredient":"I1", "weight":2, "req":False, "rating": 20, "url":"www.facebook.com"})
	# recipe_collection.insert({"recipe_name":"R2", "ingredient":"I3", "weight":3, "req":True, "rating": 20, "url":"www.facebook.com"})
	# recipe_collection.insert({"recipe_name":"R2", "ingredient":"I4", "weight":4, "req":False, "rating": 20, "url":"www.facebook.com"})

	# return recipe_collection
	return client.recipes.posts

"FIXME: query and return all ingredients."
def query_ings(recipe_collection):
	# print recipe_collection.distinct("ingredient")
	return sorted(recipe_collection.distinct("ingredient"))
	

def collecting(recipe_collection, ings):
	recipe_has_ing = {}
	recipe_require_ing = {}
	recommendation = {}
	# For every ingredient user has, get all the recipes that uses the ingredient.
	# 
	for ing in ings:
		rows = recipe_collection.find({"ingredient":ing})
		#print rows.count()
		# For every row that the ingredient is in, put the ingredient in the recipe entry in recipe_list
		for i in range(rows.count()):
			row = rows[i]
			# key is the recipe_name
			key = row["recipe_name"]
			if not recipe_has_ing.has_key(key):
				recipe_has_ing[key] = []
			recipe_has_ing[key].append(ing)
			# Add this recipe to potential recommanded recipes. initial rating is 0
			if not recommendation.has_key(key):
				recommendation[key] = 0.0

			# Add the recipe and its required ingredients to the dict
			if not recipe_require_ing.has_key(key):
				# the value is a cursor object
				recipe_require_ing[key] = recipe_collection.find({"recipe_name": key})
	return recipe_has_ing, recipe_require_ing, recommendation

def recommend_exact((recipe_has_ing, recipe_require_ing, recommendation)):
	output = {}
	# Update the ratings based on if an optional/required ing is present for each candidate recipe
	for candidate in recommendation.keys():
		total_weight = 0 # this is the total weight of ingredients of this recipe. Used for normalize
		cursor = recipe_require_ing[candidate]
		candidate_rating = 0
		candidate_url = ""
		for i in range(cursor.count()):
			#each req_ing is a row in db that this candidate recipe is related
			req_ing = cursor[i]
			candidate_rating = req_ing["rating"]
			candidate_url = req_ing["url"]
			total_weight += req_ing["weight"]
			if req_ing["ingredient"] in recipe_has_ing[candidate]:
				recommendation[candidate] += req_ing["weight"]
			# if user does not have a required ing, delete this candidate.
			elif req_ing["req"]:
				del recommendation[candidate]
				break
			else:
				continue
		# If candidate is still in recommendation list, compute the rating
		if candidate in recommendation:
			recommendation[candidate] *= 1.0*candidate_rating/total_weight
			recommendation[candidate] = int(recommendation[candidate] * 100) / 100.0
			output[(candidate, candidate_url, recommendation[candidate])] = recommendation[candidate]

	# TODO: sort the recommendation
	return sorted(output, key=output.get, reverse=True)

def recommend_with_missing((recipe_has_ing, recipe_require_ing, recommendation)):
	output = {}
	# Update the ratings based on if an optional/required ing is present for each candidate recipe
	for candidate in recommendation.keys():
		total_weight = 0 # this is the total weight of ingredients of this recipe. Used for normalize
		cursor = recipe_require_ing[candidate]
		candidate_rating = 0
		candidate_url = ""
		for i in range(cursor.count()):
			#each req_ing is a row in db that this candidate recipe is related
			req_ing = cursor[i]
			candidate_rating = req_ing["rating"]
			candidate_url = req_ing["url"]
			total_weight += req_ing["weight"]
			if req_ing["ingredient"] in recipe_has_ing[candidate]:
				recommendation[candidate] += req_ing["weight"]
			# if user does not have a required ing, don't do anything
		# If candidate is still in recommendation list, compute the rating
		if candidate in recommendation:
			recommendation[candidate] *= 1.0*candidate_rating/total_weight
			recommendation[candidate] = int(recommendation[candidate] * 100) / 100.0
			output[(candidate, candidate_url, recommendation[candidate])] = recommendation[candidate]

	# TODO: sort the recommendation
	return sorted(output, key=output.get, reverse=True)


def find_inf(TEMPLATE, html):
    index = 0
    s = html.find(TEMPLATE, index)
    data = []
    while s != -1 :
        key = ""
        s += len(TEMPLATE)
        i = 0
        while html[s+i] != '<' and html[s+i] != '"' and html[s+i] != '/':
            key += html[s+i]
            i+=1
        data.append(key)
        index = s+1
        s = html.find(TEMPLATE, index)
    return data

def page_info(url):
        response = urllib2.urlopen(url)
        html = response.read().decode('utf-8')
        data = {}
        data['ingredients'] =  find_inf('<span id="lblIngName" class="ingredient-name">', html)
        first = html.find(".jpg")
        print html[:first]
        
        while html[first] != '"':
                first -= 1
        first+=1
        url_image = ""
        while html[first] != '"':
                url_image += str(html[first])
                first += 1
                print first, html[first]
        # url_image = url_image[:len(url_image)-1]
        data['image'] = url_image
        data['description'] = find_inf('<li><span class="plaincharacterwrap break">', html)
        return data



if __name__ == "__main__":
	client = connect()
	print query_ings(set_up(client))
	ing = ["Yeast", "lkjd"]
	print query(set_up(client), ing)
	client.close()





