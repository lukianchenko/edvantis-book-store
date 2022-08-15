from flask import Flask
from flask_migrate import Migrate
from flask_swagger_ui import get_swaggerui_blueprint

from src.config import DB_URI
from src.models import db
from src.routes import rest_api

app = Flask(__name__)

"""
Swagger configs
"""
SWAGGER_URL = "/swagger"
API_URL = "/static/swagger.json"
SWAGGER_BLUEPRINT = get_swaggerui_blueprint(SWAGGER_URL, API_URL, config={"app_name": "Book store API"})

app.register_blueprint(SWAGGER_BLUEPRINT, url_prefix=SWAGGER_URL)

"""
Database initialization
"""

app.config["SQLALCHEMY_DATABASE_URI"] = DB_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
migrate = Migrate(app, db)

"""
API initialization
"""
rest_api.init_app(app)

if __name__ == "__main__":
    app.run(debug=True)
