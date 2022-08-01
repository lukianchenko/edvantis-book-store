from flask import Flask
from flask_migrate import Migrate

from src.config import DB_URI
from src.models import db

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = DB_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

migrate = Migrate(app, db)


@app.route("/")
def hello():
    return "<h1>Hello, World!</h1>"


if __name__ == "__main__":
    app.run(debug=True)
