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