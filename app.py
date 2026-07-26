from flask import Flask
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from config import Config
from src.database.models import db
login_manager = LoginManager()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    jwt.init_app(app)
    login_manager.login_view = 'auth.login'

    from src.web.routes.auth_routes import auth_bp
    from src.web.routes.main_routes import main_bp
    from src.web.routes.analysis_routes import analysis_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(analysis_bp, url_prefix='/api')

    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)