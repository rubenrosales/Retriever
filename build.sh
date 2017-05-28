#!/bin/bash
pip install virtualenv
cd flickr
virtualenv -p python2 env
source env/bin/activate
echo "Flask==0.10.1" >> requirements.txt
echo "beautifulsoup4==4.4.0" >> requirements.txt
pip install -r requirements.txt
sh run.sh
