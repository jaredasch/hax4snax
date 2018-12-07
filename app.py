import urllib, json, os# Standard Library

from flask import Flask, render_template, request, url_for,flash,session,redirect # Related third-party

from passlib.hash import md5_crypt #Local application
from util import baseHelpers as db

app = Flask(__name__)
app.secret_key = os.urandom(32)

with open('api.json', 'r') as file:
    api_dict = json.load(file)

EATSTREET_KEY = api_dict["EATSTREET_KEY"]
FOOD2FORK_KEY = api_dict["FOOD2FORK_KEY"]
MASHAPE_KEY = api_dict["MASHAPE_KEY"]

#test for a bad key then stop the app if it doesnt work
try:#as we incorporate more api just insert something that works when the api key works so when a bad key is used we'll know
    req_url = "https://api.eatstreet.com/publicapi/v1/restaurant/search?method=both&pickup-radius=100&search=pancake&street-address=26+E+63rd+St,+New+York,+NY+10065c"
    header = {"User-agent": "curl/7.43.0", "Accept": "application/json", "X-Access-Token": EATSTREET_KEY}

    req = urllib.request.Request(req_url, headers = header) # here we connect to the Zomato API to get restaurant info
    json_response = json.loads(urllib.request.urlopen(req).read())
except:
    print(" * Api key not valid!")
    exit()

# Enum values for inserting favorites into db
RESTAURANT = 0;
RECIPE = 1;

# Name, Address, Average Cost for Two, IFrame Menu, Thumbnail for Restaurant Car

def loggedIn():
    # check if user is logged in (True if yes, False if not)
    return "username" in session


@app.route("/") # Landing page
def index():
    # Our default home page before a user is logged in is to display the most popular restaurants
    req_url = "https://api.eatstreet.com/publicapi/v1/restaurant/search?method=both&pickup-radius=100&search=pancake&street-address=26+E+63rd+St,+New+York,+NY+10065c"
    header = {"User-agent": "curl/7.43.0", "Accept": "application/json", "X-Access-Token": EATSTREET_KEY}
    req = urllib.request.Request(req_url, headers = header) # here we connect to the Zomato API to get restaurant info
    json_response = json.loads(urllib.request.urlopen(req).read())
    restaurant = json_response['restaurants'][:30]

    popular_restaurants = [{"title": restaurant["name"],
                            "img": restaurant["logoUrl"],
                            "link": url_for("restaurant", id=restaurant["apiKey"]),
                            "desc": ("%s<br><strong>Tags: </strong> %s") % (restaurant["streetAddress"], ", ".join(str(x) for x in restaurant["foodTypes"]))}
                            for restaurant in json_response["restaurants"]]
    return render_template('index.html', results=popular_restaurants, user=session.get("username"))

    #print (restaurant)
    #return ("wow")

@app.route("/login") # Login Page
def login():
    if loggedIn():
        # if the user is logged in already, it will redirect them to the home page
        return redirect(url_for('index'))
    # if the user is not logged in, it renders the static login template
    return render_template('login.html')


@app.route("/auth", methods = ["POST"]) # Authentification Page
def auth():
    user_data = db.get_all_user_data()
    username=request.form.get("username") # Get Username
    password=request.form.get("password") # Get Password

    if username in user_data: # check if the username is a valid username
        if md5_crypt.verify(password, user_data[username]): # check if the password aligns with the username
            session["username"] = username # login the user
        else:
            flash("Invalid password") # display error message
    else:
        flash("Invalid username") # display error message
    return redirect(url_for('login')) # send back to login page


@app.route("/register") # Register Page
def register():
    # renders the static register page
    return render_template("register.html")


@app.route("/registerAuth", methods = ["POST"])
def registerAuth(): # Register Authentification Page

    username = request.form.get("username")
    password = request.form.get("password")
    password2 = request.form.get("password2")
    # Get form input
    user_data = db.get_all_user_data()
    if username in user_data: # check if user already exists
        flash("Username already exists")
        return redirect(url_for("register"))

    elif password != password2: # check to make sure the passwords match
        flash("Input Same Password in Both Fields!")
        return redirect(url_for("register"))
    else: # Create new user
        db.add_user(username, md5_crypt.encrypt(password))
        flash("Successfully Registered, Now Sign In!")
        return redirect(url_for('login'))


@app.route("/logout") # Logout Function
def logout():
    if not loggedIn(): # Check if the user is logged in
        flash("You tried to log out without being logged in")
        return redirect(url_for("index"))
    session.pop("username") # Remove user from session if they were logged in
    return redirect(url_for("index"))


@app.route("/search", methods = ["POST"]) # Searching Functionality
def search():
    query = urllib.parse.quote(request.form.get("query"))
    results = []
    if request.form.get("restaurants"):
        req_url = "https://api.eatstreet.com/publicapi/v1/restaurant/search?method=both&pickup-radius=100&search="+query+"&street-address=26+E+63rd+St,+New+York,+NY+10065c"
        header = {"User-agent": "curl/7.43.0", "Accept": "application/json", "X-Access-Token": EATSTREET_KEY}
        req = urllib.request.Request(req_url, headers = header)
        json_response = json.loads(urllib.request.urlopen(req).read())
        restaurant = json_response['restaurants'][:30] # limited to thirty, to not overwhelm the user upon first glance
        # load the list of popular restaurants
        popular_restaurants = [{"title": restaurant["name"],
                                "img": restaurant["logoUrl"],
                                "link": url_for("restaurant", id=restaurant["apiKey"]),
                                "desc": ("%s<br><strong>Tags: </strong> %s") % (restaurant["streetAddress"], ", ".join(str(x) for x in restaurant["foodTypes"]))}
                                for restaurant in json_response["restaurants"]]
        return render_template('index.html', results=popular_restaurants, user=session.get("username"))
    #----------------------------------------------------------------------
    if request.form.get("recipes"):
        req_url = 'https://spoonacular-recipe-food-nutrition-v1.p.mashape.com/recipes/search?instructionsRequired=true&limitLicense=false&number=20&offset=0&query=' + query
        headers = {"X-Mashape-Key": MASHAPE_KEY, "Accept": "application/json", "User-agent": "curl/7.43.0"}
        req = urllib.request.Request(req_url, headers = headers)
        json_response = json.loads(urllib.request.urlopen(req).read())
        recipes = [{"title": recipe["title"],
                    "img": json_response["baseUri"] + recipe["imageUrls"][0],
                    "link": url_for("recipe", id=recipe["id"]),
                    "desc": ("%s minutes<br>Serves %s") % (recipe["readyInMinutes"], recipe["servings"])}
                    for recipe in json_response["results"]]
        results.extend(recipes)
    return render_template('index.html', results=results);


@app.route("/restaurant/<id>") # Restaurant Card Depiction
def restaurant(id):
    req_url =  'https://api.eatstreet.com/publicapi/v1/restaurant/'+id
    header = {"User-agent": "curl/7.43.0", "Accept": "application/json", "X-Access-Token": EATSTREET_KEY}
    req = urllib.request.Request(req_url, headers = header)
    json_response = json.loads(urllib.request.urlopen(req).read())

    location = json_response["restaurant"]

    #retrieves location data of restaurant
    loc = location['streetAddress'] +", "+ location['city'] + ", "+ location['state']+ " " + location['zip']
    #----------------------------------------------------------------------
    req_url = 'https://api.eatstreet.com/publicapi/v1/restaurant/'+id+'/menu'
    header = {"User-agent": "curl/7.43.0", "Accept": "application/json", "X-Access-Token": EATSTREET_KEY}
    req = urllib.request.Request(req_url, headers = header)
    json_response = json.loads(urllib.request.urlopen(req).read())
    #retrieves menu items
    base_menu = {}
    for type in json_response:
        base_menu[type["name"]] = type["items"]
    menu_items = []
    for category in base_menu:
        for item in base_menu[category]:
            print (item)
            menu_items.append({"title" : item["name"], "price": '${:,.2f}'.format(item["basePrice"]), "description": None } )
            if 'description' in item:
                menu_items[0].update({"description" :item['description']})
    favorited = db.isFavorited(session.get('username'),id) # Whether the restaurant is a favorite or not
    return render_template('restaurants.html',
                            name = location['name'],
                            address = loc,
                            menu = base_menu,
                            img = location['logoUrl'],
                            id = id,
                            user = session.get("username"),
                            favorited = favorited)
@app.route("/favoriteRes/<id>") # Favoriting mechanism for Restaurants
def favoriteRes(id):
    if loggedIn():
        db.add_favorite(session.get("username"),id,RESTAURANT)

    return redirect("/restaurant/"+str(id))

@app.route("/favoriteRecipe/<id>") # Favoriting mechanism for Recipes
def favoriteRecipe(id):
    if loggedIn():
        db.add_favorite(session.get("username"),id,RECIPE)

    return redirect("/recipe/"+str(id))

@app.route("/unfavoriteRes/<id>") # Un-favoriting mechanism for Restaurants
def unfavoriteRes(id):
    db.remove_fav(session.get('username'),id)
    return redirect("/restaurant/"+str(id))

@app.route("/unfavoriteRecipe/<id>") # Un-favoriting mechanism for Recipes
def unfavoriteRecipe(id):
    db.remove_fav(session.get('username'),id)
    return redirect("/recipe/"+str(id))


@app.route("/favorite")
def favorite(): # Favorites Page
    #fetch ids and their associated apis
    idApiDict = db.get_idApi_dict(session.get('username'))
    #dict for the recipes to be input into the favorites page
    recipeDict = {}
    #dict for the restaurants to be input into the favorites page
    resDict = {}
    for id in idApiDict:
        if idApiDict[id] == RESTAURANT: # check whether this is a restaurant or not
            req_url =  'https://api.eatstreet.com/publicapi/v1/restaurant/'+id
            header = {"User-agent": "curl/7.43.0", "Accept": "application/json", "X-Access-Token": EATSTREET_KEY}
            req = urllib.request.Request(req_url, headers = header)
            json_response = json.loads(urllib.request.urlopen(req).read())

            location = json_response["restaurant"]
            #puts the name id and picure url into a dict
            resDict[location['name']] = (id,location['logoUrl'])
        else:#it the recipe api
            headers = {"X-Mashape-Key": MASHAPE_KEY, "Accept": "application/json", "User-agent": "curl/7.43.0"}
            req_url = 'https://spoonacular-recipe-food-nutrition-v1.p.mashape.com/recipes/' + id + '/information'
            req = urllib.request.Request(req_url, headers = headers)
            info = json.loads(urllib.request.urlopen(req).read())
            recipeDict[info["title"]] = (id, info["image"])

    return render_template('favorite.html',
                            user = session.get("username"),#So navbar changes when logged in
                            resDict = resDict,#restuarant dict
                            recipeDict = recipeDict
                            )

@app.route("/recipe/<id>") # Recipe Card Depiction
def recipe(id):
    headers = {"X-Mashape-Key": MASHAPE_KEY, "Accept": "application/json", "User-agent": "curl/7.43.0"}

    instructions_url = 'https://spoonacular-recipe-food-nutrition-v1.p.mashape.com/recipes/' + id + '/analyzedInstructions'
    instructions_req = urllib.request.Request(instructions_url, headers = headers)
    instructions = json.loads(urllib.request.urlopen(instructions_req).read()) # the recipe instructions

    summary_url = 'https://spoonacular-recipe-food-nutrition-v1.p.mashape.com/recipes/' + id + '/summary'
    summary_req = urllib.request.Request(summary_url, headers = headers)
    summary = json.loads(urllib.request.urlopen(summary_req).read()) # the recipe blurb

    ingredients_url = 'https://spoonacular-recipe-food-nutrition-v1.p.mashape.com/recipes/' + id + '/information'
    ingredients_req = urllib.request.Request(ingredients_url, headers = headers)
    ingredients = json.loads(urllib.request.urlopen(ingredients_req).read()) # the recipe ingredients

    favorited = db.isFavorited(session.get('username'),id) # Check whether the recipe is favorited
    #used to right nabar depending on logged in or not
    user = session.get('username')

    return render_template("recipe.html", favorited = favorited, user=user, summary=summary, instructions=instructions[0]["steps"], ingredients = ingredients["extendedIngredients"])


if __name__ == "__main__" : # Run the App
    app.debug = True
    app.run()
