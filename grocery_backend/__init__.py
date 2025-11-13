from flask import Flask
from flask_cors import CORS
from .config import ALLOWED_ORIGINS, API_PREFIX


def create_app():
    app = Flask(__name__)
    app.url_map.strict_slashes = False
    CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000", "allow_headers": ["Authorization", "Content-Type", "X-Custom-Api-Key", "userId", "zipCode"]}})

    # Import all blueprints
    from .routes.items import items_bp
    from .routes.previous import previous_bp
    from .routes.suggestions import suggestions_bp
    from .routes.auth import auth_bp
    from .routes.locations import locations_bp

    # Register all with the same prefix
    blueprints = [
        (items_bp, '/items'),
        (previous_bp, '/previous'),
        (suggestions_bp, '/suggestions'),
        (auth_bp, '/auth'),
        (locations_bp, '/locations')
    ]
    
    for blueprint, path in blueprints:
        app.register_blueprint(blueprint, url_prefix=f'{API_PREFIX}{path}')


    return app