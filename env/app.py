from flask import Flask, render_template, request, redirect
import model
import secret
import requests
from plotly.offline import plot
from plotly.graph_objs import Scatter
from flask import Markup
import sqlite3

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/category")
def category():
	return render_template("category.html", city_name=model.city_name)


@app.route("/init", methods=["POST"])
def init():
	city_name=request.form["city_name"]
	model.init(city_name)
	model.insert_table_from_scrap(city_name)
	return redirect('/category')


@app.route("/category_result",methods=["POST","GET"])
def category_result():
	category=request.form['category_name']
	baseurl='https://api.yelp.com/v3/businesses/search'
	headers={'Authorization': 'Bearer %s' % secret.api_key}
	params={}
	params['location']=model.city_name
	params['categories']=category
	results=model.make_request_using_cache(baseurl,headers,params)
	model.insert_table_from_api(results,category)
	conn = sqlite3.connect('final507.sqlite')
	cur = conn.cursor()
	statement='select r.lati,r.logi,r.name,r.id from restaurants_info as r join city_info as c  on c.Id=r.city where r.category=? and c.name =? limit 20'
	cur.execute(statement,(category, model.city_name))
	result=cur.fetchall()
	data,layout=model.plot_prepare(result)
	fig = dict(data=data, layout=layout )
	my_plot_div = plot(fig, include_plotlyjs=False, output_type='div')
	statement='select * from city_info where name=?'
	cur.execute(statement,[model.city_name])
	city_information=cur.fetchone()
	conn.close()
	return render_template("category_visul.html", city_information=city_information, category=category, city_name=model.city_name, div_placeholder=Markup(my_plot_div))


@app.route("/open_now",methods=["POST","GET"])
def open_now():
	baseurl='https://api.yelp.com/v3/businesses/search'
	headers={'Authorization': 'Bearer %s' % secret.api_key}
	params={}
	params['location']=model.city_name
	params['open_now']=True
	results=model.make_request_using_cache(baseurl,headers,params)
	model.insert_table_from_api(results)
	conn = sqlite3.connect('final507.sqlite')
	cur = conn.cursor()
	statement='select r.lati,r.logi,r.name,r.id from restaurants_info as r join city_info as c on c.Id=r.city where r.is_open=1 and c.name=? limit 20'
	cur.execute(statement,[model.city_name])
	result=cur.fetchall()
	data,layout=model.plot_prepare(result)
	fig = dict(data=data, layout=layout )
	my_plot_div = plot(fig, include_plotlyjs=False, output_type='div')
	statement='select * from city_info where name=?'
	cur.execute(statement,[model.city_name])
	city_information=cur.fetchone()
	conn.close()
	print(result)
	return render_template("open_now.html", city_information=city_information, city_name=model.city_name, div_placeholder=Markup(my_plot_div))


@app.route("/delivery",methods=["POST","GET"])
def delivery():
	conn = sqlite3.connect('final507.sqlite')
	cur = conn.cursor()
	statement='select r.lati,r.logi,r.name,r.id from restaurants_info as r join city_info as c on c.Id=r.city where r.delivery=1 and c.name=? limit 20'
	cur.execute(statement,[model.city_name])
	result=cur.fetchall()
	data,layout=model.plot_prepare(result)
	fig = dict(data=data, layout=layout )
	my_plot_div = plot(fig, include_plotlyjs=False, output_type='div')
	statement='select * from city_info where name=?'
	cur.execute(statement,[model.city_name])
	city_information=cur.fetchone()
	conn.close()
	print(result)
	return render_template("delivery.html", city_information=city_information, city_name=model.city_name, div_placeholder=Markup(my_plot_div))


@app.route("/price_range")
def price_range():
	return render_template("price_range.html", city_name=model.city_name)


@app.route("/price_range_result",methods=["POST","GET"])
def price_range_result():
	price=request.form['price']
	baseurl='https://api.yelp.com/v3/businesses/search'
	headers={'Authorization': 'Bearer %s' % secret.api_key}
	params={}
	params['location']=model.city_name
	params['price']=price
	results=model.make_request_using_cache(baseurl,headers,params)
	print(results)
	model.insert_table_from_api(results)
	conn = sqlite3.connect('final507.sqlite')
	cur = conn.cursor()
	statement='select r.lati,r.logi,r.name,r.id from restaurants_info as r join city_info as c on c.Id=r.city where r.price=? and c.name =? limit 20'
	if int(price)==1:
		the_price='$'
	elif int(price)==2:
		the_price='$$'
	elif int(price)==3:
		the_price='$$$'
	else:
		the_price='$$$$'
	print(the_price)
	cur.execute(statement,(the_price, model.city_name))
	result=cur.fetchall()
	data,layout=model.plot_prepare(result)
	fig = dict(data=data, layout=layout )
	my_plot_div = plot(fig, include_plotlyjs=False, output_type='div')
	statement='select * from city_info where name=?'
	cur.execute(statement,[model.city_name])
	city_information=cur.fetchone()
	conn.close()
	print(result)
	return render_template("price_range_visul.html", city_information=city_information, city_name=model.city_name, div_placeholder=Markup(my_plot_div))


if __name__ == '__main__':
	app.run(debug=True)