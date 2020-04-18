from flask import Flask
from flask import render_template
from flask import request

from utils import *

app = Flask(__name__, static_url_path="/static")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/", methods=["POST"])
def my_form_post():
    title = request.form["text"]
    processed_text = title.upper()

    ratings, title = get_ratings(title=title)

    xml_content = get_data(title=title)

    colors = get_colors(ratings)
    plot_matrix(ratings, colors, title=title)
    plot_rating_per_season(ratings, title)
    plot_scattered_ratings_per_season(ratings, title)

    series = {
        "title": processed_text,
        "plot": xml_content["plot"],
        "imdb_rating": xml_content["imdb_rating"],
        "year": xml_content["year"],
        "imdb_votes": xml_content["imdb_votes"],
        "poster": "/static/{}.png".format(title),
        "matrix": "/static/{}_rating_matrix.png".format(title),
        "ratings": "/static/{}_rating_per_season.png".format(title),
        "scattered": "/static/{}_scattered_rating_per_season.png".format(title),
    }

    return render_template("result.html", series=series)
