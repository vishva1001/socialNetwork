# Web based entity search and analysis app
Neo4j, Flask, Gunicorn

This is a web application running on an AWS EC2 instance, deployed on Gunicorn standalone WSGI server 

**to visit the app, go to this url "http://13.58.210.215:5000/"**


About files in this repo:

-socialNetwork.py: clean, consolidate and load data to graph database

-app.py:			      the main python app, where all functions and redirections are defined

-static:			      stores static content for the webapp (images, stylesheets, scripts)  

-templates:		    stores the views ie. html pages

 ---search.html:	  landing page of our web app
 
-test.py:			    unit tests for the web app

-wsgi.py:		      configuration to run app with wsgi

-requirements.txt:	lists all packages required to run the app
