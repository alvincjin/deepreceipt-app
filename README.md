DeepFit Web App
=========
This is a web app for real estate sellers and buyers.
Dealers and sellers can list houses on this web app.
Buyers can search houses based on their perferences.
Then, contact with dealers and sellers for appointments.

This app is implemented by Flask framework in Python 2.7.

Install and Run the App:

```
$ cd RealEstateApp

$ virtualenv venv

$ source venv/bin/activate

$ pip install -r requirements.txt
```

Database Management
```
# Initialize migration package
$ ./manage.py db init

# Create DB change scripts
$ ./manage.py db migrate

# Execute DB changes
$ ./manage.py db upgrade

$ python run.py

```
