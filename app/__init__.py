import os

from flask import Flask
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY") 

    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    if not app.debug:
        app.config["SESSION_COOKIE_SECURE"] = True

    #registering route file
    from app.routes.auth import auth_bp
    from app.routes.links import links_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(links_bp)


    return app


 

