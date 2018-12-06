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
                            "desc": ("%s<br><strong>Tags: </strong> %s") % (restaurant["streetAddress"], restaurant["foodTypes"])}
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
    query = request.form.get("query")
    results = []
    if request.form.get("restaurants"):
        req_url = "https://api.eatstreet.com/publicapi/v1/restaurant/search?method=both&pickup-radius=100&search="+query+"&street-address=26+E+63rd+St,+New+York,+NY+10065c"
        header = {"User-agent": "curl/7.43.0", "Accept": "application/json", "X-Access-Token": EATSTREET_KEY}
        req = urllib.request.Request(req_url, headers = header)
        json_response = json.loads(urllib.request.urlopen(req).read())
        restaurant = json_response['restaurants'][:30]

        popular_restaurants = [{"title": restaurant["name"],
                                "img": restaurant["logoUrl"],
                                "link": url_for("restaurant", id=restaurant["apiKey"]),
                                "desc": ("%s<br><strong>Tags: </strong> %s") % (restaurant["streetAddress"], restaurant["foodTypes"])}
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


@app.route("/restaurant/<id>") # Temporary Restaurant Card Depiction
def restaurant(id):
    req_url =  'https://api.eatstreet.com/publicapi/v1/restaurant/'+id
    header = {"User-agent": "curl/7.43.0", "Accept": "application/json", "X-Access-Token": EATSTREET_KEY}
    req = urllib.request.Request(req_url, headers = header)
    json_response = json.loads(urllib.request.urlopen(req).read())

    location = json_response["restaurant"]

    #retrieves location data of restaurant
    loc = location['streetAddress'] +" "+ location['city'] + ", "+ location['state']+ " " + location['zip']
    #----------------------------------------------------------------------
    req_url = 'https://api.eatstreet.com/publicapi/v1/restaurant/'+id+'/menu'
    header = {"User-agent": "curl/7.43.0", "Accept": "application/json", "X-Access-Token": EATSTREET_KEY}
    req = urllib.request.Request(req_url, headers = header)
    json_response = json.loads(urllib.request.urlopen(req).read())

    #retrieves menu items
    base_menu = json_response[0]["items"]
    # print(base_menu)
    menu_items = []
    for item in base_menu:
        #print (item)
        menu_items.append({"title" : item["name"], "price": '${:,.2f}'.format(item["basePrice"]), "description": None } )

        if 'description' in item:
            menu_items[0].update({"description" :item['description']})
    # print (menu_items)
    #if description in
    #av = str(json_response['average_cost_for_two']) + json_response['currency']
    return render_template('restaurants.html',
                            name = location['name'],
                            address = loc,
                            menu = menu_items,
                            img = location['logoUrl'])
                            #img = json_response['thumb'])



@app.route("/recipe/<id>") # Temporary Recipe Card Depiction
def recipe(id):
    req_url = 'https://spoonacular-recipe-food-nutrition-v1.p.mashape.com/recipes/' + id + '/analyzedInstructions'
    headers = {"X-Mashape-Key": MASHAPE_KEY, "Accept": "application/json", "User-agent": "curl/7.43.0"}
    req = urllib.request.Request(req_url, headers = headers)
    json_response = json.loads(urllib.request.urlopen(req).read())
    return "In Progress"


if __name__ == "__main__" : # Run the App
    app.debug = True
    app.run()
