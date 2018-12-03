# hax4snax

*A*mit Narang, *J*ared Asch, *M*aggie Zhao, *P*eter Cwalina

# Brief Summary of Project

Our project will recommend recipes to users based off of their cravings. They can search up an ingredient, dish, restaurant, or type of cuisine and get a collection of recipes that would fit their needs. If we have additional time to build our project, we will integrate a third, shopping API in order to give our users a total ingredient cost for making a certain dish, and perhaps offer that as a ranking option.

# Dependencies

Runs with Python3, flask, wheel
Also uses SQLite3, which comes with Python3

Uses [passlib](https://passlib.readthedocs.io/en/stable/ "passlib documentation"), a library of password hashing functions.
Storing user passwords as plaintext is a massive security vunerability and should be avoided, but implementing password hashing ourselves was not viable given time constraints. Passlib is used to enter hashed passwords into database when users register, and check passwords when users try to login.

# To run our project:

1. Clone this repository

```
$ git clone https://github.com/narang-amit/hax4snax.git
```

2. Create & Activate your virtual environment

```
$ python3 -m venv tm
$ . tm/bin/activate
```

3. In your activated virtual environment, run the following commmands to install the Dependencies

```
(tm) $ pip3 install wheel
(tm) $ pip3 install flask
(tm) $ pip3 install passlib
```

4. Go to the folder

```
(tm) $ cd hax4snax
```

5. Edit the .json file called api.json and insert your api keys accordingly

```
"ZOMATO_KEY":"<insert key here>",
"FOOD2FORK_KEY": "<insert key here>"
```

5. Secure the API keys.

  a) Navigate to https://developers.zomato.com/api, create an account, generate an API key, and insert it into zomapi.txt
  b) Navigate to https://www.food2fork.com/default/user/register?_next=%2Fuser%2Fapi, create an account, generate an API key, and insert it into f2fapi.txt

5. Run app.py

```
(tm) $ python app.py
```

6. Navigate to `localhost:5000` on your web browser
