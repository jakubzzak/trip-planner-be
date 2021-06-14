Trip planner - to make your trip planning a little bit more fun
==

[built in Flask, MongoDb and React]

### create virtual environment

Navigate to the root of your folder and create virtual environment with the following command:

``python3 -m venv venv/``

Activate your virtual environment like this:

``source venv/bin/activate``

To deactivate it run:

``deactivate``

After activating your virtual environment install all required dependencies:

``pip install -r requirements.txt``

If adding new dependency, run the following command to add the dependency to the requirements file:

``pip freeze > requirements.txt``

### .env

create your local .env file in the same directory as config.py and add all required values that Config class is expecting to receive


### run

To run the server in your terminal navigate to the root of the folder and run this command:

``python3 app.py``
