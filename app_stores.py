# go into each app, and pull other info?
# how often to do breaks? to not slam servers and get banned?

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import os
from robobrowser import RoboBrowser

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
#app.config['SQLALCHEMY_ECHO'] = True # prints interactions w the db
db = SQLAlchemy(app)

charts = {
	'Top Free in Android Apps': 'https://play.google.com/store/apps/collection/topselling_free',
	'Top Paid in Android Apps': 'https://play.google.com/store/apps/collection/topselling_paid',
	'Top Grossing Android Apps': 'https://play.google.com/store/apps/collection/topgrossing',
	'Top Free in Games': 'https://play.google.com/store/apps/category/GAME/collection/topselling_free',
	'Top Paid in Games': 'https://play.google.com/store/apps/category/GAME/collection/topselling_paid',
	'Top Grossing Games': 'https://play.google.com/store/apps/category/GAME/collection/topgrossing'}

class App(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	rank = db.Column(db.Integer)
	stars = db.Column(db.Numeric(2,1, asdecimal = False))
	price = db.Column(db.Numeric(6,2, asdecimal = False))
	description = db.Column(db.Text)
	title = db.Column(db.String(80))
	chart = db.Column(db.String(80))
	timestamp = db.Column(db.DateTime) # tried to make this primary key, but Ashish said Flask or SQLAlchemy doesn't like that
	store = db.Column(db.String(80))

	def __init__(self, rank, stars, price, description, title, chart, timestamp, store):
		self.rank = rank
		self.stars = stars
		self.price = price
		self.description = description
		self.title = title
		self.chart = chart
		self.timestamp = timestamp
		self.store = store

	def __repr__(self):
	    return '<{}>'.format(self.timestamp)

def google_play():
	for chart_name in charts.keys():
		r = requests.get(charts[chart_name])
		soup = BeautifulSoup(r.content, 'html.parser') # lxml is not lenient enough; haven't tried html5lib

		counter = 0

		for app in soup.find_all(class_= "card no-rationale square-cover apps small"):
			counter += 1
			print counter
			price = unicode(app.find(class_ = 'price buy').span.string)

			if price == u'Free':
				price = float(0)
			elif price == None:
				pass
			else:
				price = float(price[1:])

			db_entry = App(
				counter, 
				float(app.find(class_ = 'reason-set-star-rating').contents[1]['aria-label'][7:10]), 
				price, 
				unicode(app.find(class_ = 'description')), 
				app.find(class_ = 'title')['title'], 
				chart_name,
				datetime.now(),
				'Google Play')

			db.session.add(db_entry)
	
	db.session.commit()

def test():
	db_entry = App(
		123, 
		3.5, 
		None, 
		'some description', 
		'soem title', 
		'chart_name',
		datetime.now(),
		'Google Play')

	db.session.add(db_entry)
	db.session.commit()

	print App.query.all()

# could also make a decorated fn
# or make arguments ('if german, inject this code')
def german_google_play():
	for chart_name in charts.keys():
		browser = RoboBrowser(history=True, parser='html.parser')
		browser.open('http://ciproxy.de/browse.php?u=' + charts[chart_name])

		form = browser.get_form(action='includes/process.php')
		browser.submit_form(form)

		counter = 0

		for app in browser.find_all(class_= "card no-rationale square-cover apps small"):
			counter += 1
			print counter
			price = unicode(app.find(class_ = 'price buy').span.string)

			if price == u'Free' or price == u'None':
				price = float(0)
			else:
				temp = price.split(',')
				price = float(temp[0] + '.' + temp[1][:2])

			stars = app.find(class_ = 'reason-set-star-rating').contents[1]['aria-label'][4:7]
			stars = stars[0] + '.' + stars[2]

			db_entry = App(
				counter, 
				float(stars), 
				price, 
				unicode(app.find(class_ = 'description')), 
				app.find(class_ = 'title')['title'], 
				chart_name,
				datetime.now(),
				'Google Play Germany')

			db.session.add(db_entry)

	db.session.commit()