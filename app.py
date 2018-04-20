from flask import Flask, render_template, request, redirect
import model

app = Flask(__name__)

@app.route("/")
def index():
    ## print the guestbook
    return render_template("index.html")

@app.route("/category")
def category():
	return render_template("category.html",  city_name=model.city_name)

@app.route("/init", methods=["POST"])
def init():
	city_name=request.form['city_name']
	model.init(city_name)
	return redirect('/category')

@app.route("/category_result",methods=["POST"])
def category_result():
	city_name=model.city_name
	request.form['category_name']
	##some code for search and cache
	return render_template("category_visul.html")


if __name__ == '__main__':
	app.run(debug=True)