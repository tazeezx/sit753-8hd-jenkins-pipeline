import os
from flask import Flask, render_template, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "Movies.db"))

from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = database_file
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
metrics = PrometheusMetrics(app)

class Movie(db.Model):
    title = db.Column(db.String(80), unique=True, nullable=False, primary_key=True)
    year = db.Column(db.Integer, nullable=True)
    rating = db.Column(db.Float, nullable=True)

    def __repr__(self):
        return "<Title: {}>".format(self.title)


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST" and request.form.get("title"):
        try:
            movie = Movie(
                title=request.form.get("title"),
                year=request.form.get("year", type=int),
                rating=request.form.get("rating", type=float),
            )
            db.session.add(movie)
            db.session.commit()
        except Exception:
            db.session.rollback()
    movies = Movie.query.all()
    return render_template("index.html", movies=movies)


@app.route("/update", methods=["POST"])
def update():
    newtitle = request.form.get("newtitle")
    oldtitle = request.form.get("oldtitle")
    movie = Movie.query.filter_by(title=oldtitle).first()
    if movie:
        movie.title = newtitle
        if request.form.get("year"):
            movie.year = request.form.get("year", type=int)
        if request.form.get("rating"):
            movie.rating = request.form.get("rating", type=float)
        db.session.commit()
    return redirect("/")


@app.route("/delete", methods=["POST"])
def delete():
    title = request.form.get("title")
    movie = Movie.query.filter_by(title=title).first()
    if movie:
        db.session.delete(movie)
        db.session.commit()
    return redirect("/")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run("0.0.0.0", debug=os.environ.get("FLASK_DEBUG", "false").lower() == "true")