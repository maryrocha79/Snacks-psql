from flask import Flask, render_template, request, redirect, url_for
from flask_modus import Modus
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy

DB = "postgresql://localhost/snacks_database"

app = Flask(__name__)
app.config['SECRET_KEY'] = "abc123"
Modus(app)
toolbar = DebugToolbarExtension(app)

app.config['SQLALCHEMY_DATABASE_URI'] = DB
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)


class Snack(db.Model):
    __tablename__ = "snacks"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    kind = db.Column(db.Text)


# create tables as needed
db.create_all()


@app.route("/snacks", methods=["GET"])
def index():
    """Show all snacks."""

    snacks = Snack.query.all()  # [<Snack>, <Snack>]
    return render_template("index.html", snacks=snacks)


@app.route("/snacks/new", methods=["GET"])
def new():
    return render_template("new.html")


@app.route("/snacks", methods=["POST"])
def create():
    name = request.form['name']
    kind = request.form['kind']
    new_snack = Snack(name=name, kind=kind)

    db.session.add(new_snack)  # makes INSERT happen
    db.session.commit()
    return redirect(url_for("index"))


@app.route("/snacks/<int:id>", methods=["GET"])
def show(id):
    """Info on a snack."""

    # try:
    # .one raises if doesn't exist
    # snack = Snack.query.filter(Snack.id == id).one()  # <Snack>
    # .first, doesn't raise error if not found, returns first matching
    snack = Snack.query.filter(Snack.id == id).first()  # <Snack>
    if snack is None:
        return "oops, cannot find"
        # return redirect(url_for("page_not_found"))
    print("debug show", snack)

    return render_template("show.html", snack=snack)


@app.route("/snacks/<int:id>", methods=["DELETE"])
def destroy(id):
    snack = Snack.query.filter(Snack.id == id).one()
    db.session.delete(snack)
    db.session.commit()
    return redirect(url_for("index"))


@app.route("/snacks/<int:id>/edit", methods=["GET"])
def edit(id):
    snack = Snack.query.filter(Snack.id == id).one()
    return render_template("edit.html", snack=snack)


@app.route("/snacks/<int:id>", methods=["PATCH"])
def update(id):
    name = request.values.get('name')
    kind = request.values.get('kind')

    snack = Snack.query.filter(Snack.id == id).one()
    snack.name = name
    snack.kind = kind

    db.session.commit()
    return redirect(url_for("index"))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
