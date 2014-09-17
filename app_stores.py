# go into each app, and pull other info?
# how often to do breaks? to not slam servers and get banned?

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from flask.ext.sqlalchemy import SQLAlchemy

charts = {
	'Top Free in Android Apps': 'https://play.google.com/store/apps/collection/topselling_free',
	'Top Paid in Android Apps': 'https://play.google.com/store/apps/collection/topselling_paid',
	'Top Grossing Android Apps': 'https://play.google.com/store/apps/collection/topgrossing',
	'Top Free in Games': 'https://play.google.com/store/apps/category/GAME/collection/topselling_free',
	'Top Paid in Games': 'https://play.google.com/store/apps/category/GAME/collection/topselling_paid',
	'Top Grossing Games': 'https://play.google.com/store/apps/category/GAME/collection/topgrossing'}

#results = {}

db = SQLAlchemy(app)

for chart_name in charts.keys():
	r = requests.get(charts[chart_name])
	soup = BeautifulSoup(r.content, 'html.parser') # lxml is not lenient enough; haven't tried html5lib

	counter = 0

	for app in soup.find_all(class_= "card no-rationale square-cover apps small"):
		counter += 1
		title = app.find(class_ = 'title')['title']
		price = unicode(app.find(class_ = 'price buy').span.string)

		if price == u'Free':
			price = float(0)
		else:
			price = float(price[1:])

		"""results[datetime.now()] = {
			'rank': counter,
			'stars': float(app.find(class_ = 'reason-set-star-rating').contents[1]['aria-label'][7:10]),
			'price': price,
			'description': unicode(app.find(class_ = 'description')), # messy, contains HTML tags
			'title': title,
			'chart': chart_name}"""

		db_entry = Search(
			counter, 
			float(app.find(class_ = 'reason-set-star-rating').contents[1]['aria-label'][7:10]), 
			price, 
			unicode(app.find(class_ = 'description')), 
			title, 
			chart_name)

		db.session.add(db_entry)
		db.session.commit()	

class PutIntoDB(db.Model):
	def __init__(self, rank, stars, price, description, title, chart, datetime):
		self.rank = db.Column(db.Integer)
		self.stars = db.Column(db.Decimal(2,1))
		self.price = db.Column(db.Decimal(6,2))
		self.description = db.Column(db.String(80))
		self.title = db.Column(db.String(80))
		self.chart = db.Column(db.String(80))
		self.datetime = db.Column(db.DateTime, primary_key = True)

def turn_into_csv(results):
	import pandas as pd

	df = pd.DataFrame(results).T
	df.index.name = 'datetime'
	df = df.reset_index()

	df.drop(['description'], axis=1).to_csv('results.csv', encoding = 'utf-8', index = False, date_format = '%Y-%m-%d')

#turn_into_csv(results)