from flask import Flask
from .config import Config
from flask import render_template

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    from .auth import auth_bp
    from .users import users_bp
    from .modules import modules_bp
    from .notes import notes_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(modules_bp)
    app.register_blueprint(notes_bp)

    @app.route("/")
    def index():
        return "Hello, app"

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html"), 404

    return app

