import os
from flask import Flask

from .blueprints import index, about, map


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    app.register_blueprint(index.bp)
    app.register_blueprint(about.bp)
    app.register_blueprint(map.bp)

    return app
