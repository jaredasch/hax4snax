from flask import Flask,render_template
import urllib,json
from urllib.request import Request
app = Flask(__name__)

@app.route("/")
def root():
    return render_template('index.html')

@app.route("/recipe")
def recipe():
    desc = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
    Dictionary =	{
    "butter": "two sticks",
    "tomato sauce": "two cans",
    "linguini": "three boxes" }
    return render_template('recipe.html',
                            img = "https://www.platingsandpairings.com/wp-content/uploads/2015/10/Fresh-Linguin-with-Roasted-Fennel-4-e1446066750773.jpg",
                            dict = Dictionary,
                            description = desc)







if __name__ == "__main__" :
    app.debug = True
    app.run()
