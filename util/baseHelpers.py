import sqlite3
DB_FILE = "data/base.db"

def add_user(username,password):
    '''adds users to use table'''
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    command = "INSERT INTO users (username,password)VALUES(?,?);"
    c.execute(command,(username,password))
    db.commit()
    db.close()

def get_all_user_data():
    '''gets all user data into a dict'''
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    command  = "SELECT username,password FROM users;"
    c.execute(command)
    userInfo = c.fetchall()
    db.close()
    dict = {}
    for item in userInfo:
        dict[item[0]] = item[1]
    return dict

def getUserId(username):
    '''gets user id based on username'''
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    command = "SELECT id FROM users WHERE username = ?;"
    c.execute(command,(username,))
    user_id = c.fetchall()
    db.close()
    return user_id[0][0]

def add_favorite(username,recipe_id,api):
    '''adds a favorited recipe to the favorites table'''
    favs = get_all_user_Recipes(username)
    if recipe_id in favs:
        return
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    command = "INSERT INTO favorites VALUES(?,?,?);"
    c.execute(command,(username,recipe_id,api))
    db.commit()
    db.close()



def get_all_user_Recipes(username):
    '''gets all of a users favorited recipesids'''
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    command = "SELECT recipe_id FROM favorites WHERE username = ?;"
    c.execute(command,(username,))
    favs  = c.fetchall()
    db.close()
    fav = []
    #just turns it into a list instead of tuples
    for each in favs:
        fav.append(each[0])
    return fav

def get_all_user_Api(username):
    '''gets all of the apis associated with a recipeid in a list'''
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    command = "SELECT api FROM favorites WHERE username = ?;"
    c.execute(command,(username,))
    favs  = c.fetchall()
    db.close()
    api = []
    #just turns it into a list instead of tuples
    for each in favs:
        api = api + each[0]
    return api
def get_recipeApi_dict(username):
    '''returns a dict of recipe_id:api key:value for a particular user'''
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    command = "SELECT recipe_id,api FROM favorites WHERE username = ?;"
    c.execute(command,(username,))
    list = c.fetchall()
    db.close()
    dict = {}
    for each in list:
        dict[each[0]]=each[1]
    return dict


def remove_fav(username,recipe_id):
    '''removes a favorited recipe based on the user and its id'''
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    command = "DELETE FROM favorites WHERE username = ? AND recipe_id = ?;"
    c.execute(command,(username,recipe_id))
    db.commit()
    db.close()
