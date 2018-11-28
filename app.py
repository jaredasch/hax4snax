from flask import Flask, render_template, request, url_for
import urllib, json
app = Flask(__name__)

ZOMATO_KEY = "3188b26a3af82c1b97b152a900658fc6"
FOOD2FORK_KEY = "701c0f889e35ba76a0d6f8ae4996c21e"

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/search", methods = ["POST"])
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

@app.route("/restaurant/<id>")
def restaurant(id):
    return "Temp"

@app.route("/recipe/<id>")
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


if __name__ == "__main__" :
    app.debug = True
    app.run()
