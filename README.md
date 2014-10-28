Real Estate Web App
=========
Install App:

mkdir project_folder
cd project_folder
python virtualenv.py flask
flask/bin/pip install -r requirements.txt
flask/bin/python db_create.py
./run.py

Install Mongodb:

1. sudo apt-key adv --keyserver keyserver.ubuntu.com --recv 7F0CEB10
2. echo 'deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen' | sudo tee /etc/apt/sources.list.d/10gen.list
3. sudo apt-get update
4. sudo apt-get install mongodb-10gen

Repair for connection Error: If you are running Ubuntu, then there is an issue with folder ownership.

Run these commands:

1.  Stop mongodb service
    sudo service mongodb stop

2.  Remove mongodb lock file
    sudo rm /var/lib/mongodb/mongod.lock

3.  Change ownership from root to mongodb path
    sudo chown -R mongodb:mongodb /var/lib/mongodb/

4.  Start mongodb service
    sudo service mongodb start

5.  Test mongo app
    mongo

Test Mongodb:
1. sudo service mongodb start

2. mongo
db.test.save( { a: 1 } )
db.test.find()

3. sudo service mongodb stop



To do list:

18/6 support upload portrait for user.
User only can see "Edit" button for his posts. Pass test
19/6 separate common user and agents
20/6 create Carousel in index.html, and cancel button on edit_profile.html
21/6 modify some bootstrap,e.g. form format, split button dropdowns for action btn and edit btn; 
add house price and location in model.py and forms.py
23/6 finish perference form and model. Once add a new model, run db_create.py
	add favorite model and relationship between User and Post. User can add posts in his favorite
24/6 add basic exact search functionality and also complete the Post form, need to improve the look, and approximate search
25/6 modify the format of post, search and preference form; 
	associate interest user number on the post;
	add the post delete function, also support Cascade deleting on Favoriate Table
26/6 Add approximate search function;
	Complete agent’s profile form by adding phone, post's form by adding address
27/6 add basic geocoder and google map function
28/6 solve the embedded google map in modal window problem: but there is still delay problem, which mean after clicking a map, it corresponds to wrong post info.
	add User,Post Admin and File Admin function by flask-admin
29/6 send activation link to new registered user to active.
     Hard to show recommandation info in the top of a list. Will consider to add the email function.
30/6 Remove the dropdwon buttons, instead icon and link; add slider for bedroom No.; improve some HTML problems. 
02/7 add a reCaptcha filed in sign up form, and remove: /flask/bin/pip uninstall flask-babel, since an error between them;
     add google calendar to users, have to set the calendar as public for everyone to see.
03/7 change the way to load a model into an editable form;
     show calendar in a modal window

05/7 add a page for each home, which shows more details
06/7 improve the looking of search form; fix the map problem; fix default img problem;
     


     
          

