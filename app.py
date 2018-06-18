from flask import Flask, render_template, request, redirect, url_for
from flask_modus import Modus
import psycopg2
from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__)
Modus(app)
app.config['SECRET_KEY'] = "abc123"
toolbar = DebugToolbarExtension(app)
DB = "postgresql://localhost/snacks_database"


class Snack:
    count = 1

    def __init__(self, name, kind):
        self.name = name
        self.kind = kind
        self.id = Snack.count
        Snack.count += 1


apple = Snack("Apple", "fruit")
fig_bar = Snack("Fig Bar", "Baked Good")
tortilla_chips = Snack("Tortilla Chips", "Chips")
snacks = [apple, fig_bar, tortilla_chips]

# @app.route("/snacks", methods=["GET"])
# def index():
#     return render_template("index.html", snacks=snacks)


@app.route("/snacks", methods=["GET"])
def index():
    with psycopg2.connect(DB) as conn:
        c = conn.cursor()
        c.execute("SELECT id,name,kind FROM snacks")
        snacks = c.fetchall()
        snacks = [{"id": s[0], "name": s[1], "kind": s[2]} for s in snacks]
    return render_template("index.html", snacks=snacks)


@app.route("/snacks/new", methods=["GET"])
def new():
    return render_template("new.html")


@app.route("/snacks", methods=["POST"])
def create():
    new_snack = Snack(request.form['name'], request.form['kind'])
    snacks.append(new_snack)
    return redirect(url_for("index"))


@app.route("/snacks/<int:id>", methods=["GET"])
def show(id):
    try:
        found_snack = next(snack for snack in snacks if snack.id == id)
        return render_template("show.html", snack=found_snack)
    except Exception as e:
        return redirect(url_for("page_not_found"))


@app.route("/snacks/<int:id>", methods=["DELETE"])
def destroy(id):
    found_snack = next(snack for snack in snacks if snack.id == id)
    snacks.remove(found_snack)
    return redirect(url_for("index"))


@app.route("/snacks/<int:id>/edit", methods=["GET"])
def edit(id):
    try:
        found_snack = next(snack for snack in snacks if snack.id == id)
        return render_template("edit.html", snack=found_snack)
    except Exception as e:
        return redirect(url_for("page_not_found"))


@app.route("/snacks/<int:id>", methods=["PATCH"])
def update(id):
    found_snack = next(snack for snack in snacks if snack.id == id)
    found_snack.name = request.form['name']
    found_snack.kind = request.form['kind']
    return redirect(url_for('show', id=found_snack.id))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
