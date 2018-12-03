import urllib, json, os,sys # Standard Library

from flask import Flask, render_template, request, url_for,flash,session,redirect # Related third-party

from passlib.hash import md5_crypt #Local application
from util import baseHelpers as db


app = Flask(__name__)
app.secret_key = os.urandom(32)

ZOMATO_KEY = "3188b26a3af82c1b97b152a900658fc6"
FOOD2FORK_KEY = "701c0f889e35ba76a0d6f8ae4996c21e"

if len(sys.argv) == 3:
    print('ZomatoKey:')
    print(sys.argv[1])
    ZOMATO_KEY = sys.argv[1]
    print('Food2fork key:')
    print(sys.argv[2])
    FOOD2FORK_KEY = sys.argv[2]
    try:
        index()
        #pls insert any others funct that use api keys here
    except:
        print('You Have a bad api key')
        sys.exit()



def loggedIn():
    # check if user is logged in (True if yes, False if not)
    return "username" in session
@app.route("/") # Landing page
def index():
    # Our default home page before a user is logged in is to display the most popular restaurants
    req_url = "https://developers.zomato.com/api/v2.1/search?entity_id=280&entity_type=city&sort=rating&order=desc"
    header = {"User-agent": "curl/7.43.0", "Accept": "application/json", "user_key": ZOMATO_KEY}
    req = urllib.request.Request(req_url, headers = header) # here we connect to the Zomato API to get restaurant info
    json_response = json.loads(urllib.request.urlopen(req).read())
    popular_restaurants = [{"title": restaurant["restaurant"]["name"], "img": restaurant["restaurant"]["featured_image"], "link": url_for("restaurant", id=restaurant["restaurant"]["R"]["res_id"]), "desc": ("%s<br><strong>Tags: </strong> %s") % (restaurant["restaurant"]["location"]["address"], restaurant["restaurant"]["cuisines"])} for restaurant in json_response["restaurants"]]
    return render_template('index.html', results=popular_restaurants)

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
        req_url = "https://developers.zomato.com/api/v2.1/search?entity_id=280&entity_type=city&q=" + query
        header = {"User-agent": "curl/7.43.0", "Accept": "application/json", "user_key": ZOMATO_KEY}
        req = urllib.request.Request(req_url, headers = header)
        json_response = json.loads(urllib.request.urlopen(req).read())
        results.extend([{"title": restaurant["restaurant"]["name"], "img": restaurant["restaurant"]["featured_image"], "link": url_for("restaurant", id=restaurant["restaurant"]["R"]["res_id"]), "desc": ("%s<br><strong>Tags: </strong> %s") % (restaurant["restaurant"]["location"]["address"], restaurant["restaurant"]["cuisines"])} for restaurant in json_response["restaurants"]])
    if request.form.get("recipes"):
        req_url = "https://www.food2fork.com/api/search?" + urllib.parse.urlencode({"key": FOOD2FORK_KEY, "q": query})
        req = urllib.request.Request(req_url, headers = {"User-agent": "curl/7.43.0"})
        json_response = json.loads(urllib.request.urlopen(req).read())
        # json_response = json.loads(RECIPE_DATA) ## For testing from local data to reduce API calls
        results.extend([{"title": recipe["title"], "img": recipe["image_url"], "link": url_for("recipe", id=recipe["recipe_id"]), "desc": "from %s" % (recipe["publisher"])} for recipe in json_response["recipes"]])
    return render_template('index.html', results=results);

@app.route("/restaurant/<id>") # Temporary Restaurant Card Depiction
def restaurant(id):
    return "Temp"

@app.route("/recipe/<id>") # Temporary Recipe Card Depiction
def recipe(id):
    return "Temp"

# @app.route("/recipe")
# def recipe():
#     desc = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
#     Dictionary =	{
#     "butter": "two sticks",
#     "tomato sauce": "two cans",
#     "linguini": "three boxes" }
#     return render_template('recipe.html',
#                             img = "https://www.platingsandpairings.com/wp-content/uploads/2015/10/Fresh-Linguin-with-Roasted-Fennel-4-e1446066750773.jpg",
#                             dict = Dictionary,
#                             description = desc)

if __name__ == "__main__" : # Run the App
    app.debug = True
    app.run()
