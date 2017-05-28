Retriever
=========

Flask application that retrieves images containing a specific hashtag from Flickr and Instagram. 


Environment
------------
Tested using these configurations

OS: OS X 10.11.4
Python: 2.7.10
pip 8.1.1
Flask 0.10.1

Installation
------------

bash build.sh

This will install some necessary dependencies and will execute the program. All necessary authentication tokens must be preconfigured in flickr/secrets.cfg

Running
-----------

Running build.sh automatically starts the program but to manually start it run:

bash run.sh


Usage
-------------
http://127.0.0.1:5000/

Dependencies
-------------
Flask 0.10.1
beautifulsoup 4.4.0

Files
------------

run.py
README.md
build.sh

flickr/run.sh
flickr/requirements.txt
flickr/secrets.cfg

app/_init_.py
app/json_api.py

