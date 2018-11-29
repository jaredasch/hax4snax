import sqlite3

db = sqlite3.connect("base.db")
c = db.cursor()
#create users
command = "CREATE TABLE users(id INTEGER PRIMARY KEY AUTOINCREMENT,username TEXT UNIQUE,password TEXT)"
c.execute(command)
#create favorites
command = "CREATE TABLE favorites(username TEXT, url TEXT)"
c.execute(command)
db.commit()
db.close()
