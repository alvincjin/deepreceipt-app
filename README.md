DeepReceipt Web App
=========
This is an AI-backed Web application in Python and Flask to help customers manage expenses by uploading receipts.

It pre-processes receipt images to detect the receipt location, crop it from background, and classify the vendor logos 
by OpenCV and Deep learning technologies.

We built a ConvNN + RNN(BLSTM) + CTC Loss network model as a morden OCR(Optical Character Recognization) engine 
to extract text from receipt images by using Tensorflow.

Then, complementary analysis is applied on the OCR results to enhance/improve the recognization accuracy by artifical rules.

Finally, convert unstructure data to Json files and stored in database.

This app is implemented by Flask framework in Python 2.7.

Install and Run the App:

```
$ cd DeepReceipt

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
