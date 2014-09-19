def turn_into_csv(results):
	import pandas as pd

	df = pd.DataFrame(results).T
	df.index.name = 'datetime'
	df = df.reset_index()

	df.drop(['description'], axis=1).to_csv('results.csv', encoding = 'utf-8', index = False, date_format = '%Y-%m-%d')

results[datetime.now()] = {
	'rank': counter,
	'stars': float(app.find(class_ = 'reason-set-star-rating').contents[1]['aria-label'][7:10]),
	'price': price,
	'description': unicode(app.find(class_ = 'description')), # messy, contains HTML tags
	'title': title,
	'chart': chart_name}	

"""I had tried using decorators, but AFAIK they still don't allow access to variables on the same scope/level.
I also did this using classes, but thought it was overkill."""

def german_google_play():
	url_start = 'http://ciproxy.de/browse.php?u='
	store_name = 'Google Play Germany'

	def get_stars(app):
		stars = app.find(class_ = 'reason-set-star-rating').contents[1]['aria-label'][4:7]
		stars = stars[0] + '.' + stars[2]
		return float(stars)

	def transform_price(price):
		if price == u'Free' or price == u'None':
			return float(0)
		else:
			temp = price.split(',')
			return float(temp[0] + '.' + temp[1][:2])		

	def open_site(chart_name):
		browser = RoboBrowser(history=True, parser='html.parser')
		browser.open(url_start + charts[chart_name])

		form = browser.get_form(action='includes/process.php')
		browser.submit_form(form)

		return browser

	google_play(open_site, get_stars, transform_price, store_name)

def american_google_play():
	store_name = 'Google Play US'

	def get_stars(app):
		return float(app.find(class_ = 'reason-set-star-rating').contents[1]['aria-label'][7:10])

	def transform_price(price):
		if price == u'Free' or price == u'None':
			return float(0)
		else:
			temp = price.split(',')
			return float(price[1:])

	def open_site(chart_name):
		browser = RoboBrowser(history=True, parser='html.parser')
		browser.open(charts[chart_name])

		return browser

	google_play(open_site, get_stars, transform_price, store_name)

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

