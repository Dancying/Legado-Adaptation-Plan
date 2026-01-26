from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from app.routes import legado_api


def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(legado_api)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1)
    return app
