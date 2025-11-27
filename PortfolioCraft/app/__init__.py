from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from dotenv import load_dotenv
import os


db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app():
   
    load_dotenv()

   
    app = Flask(__name__)
    
   
    app.config.from_object('config.Config')
    app.config['SECRET_KEY'] = os.getenv('d450bdbcb14519d61944754072de3736ade171a9dad49ed7') or 'devkey'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI') or 'sqlite:///../instance/portfolio.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'  # default login view for @login_required

    
    from .models import User

    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    
    from .routes import main as main_bp
    from .admin import admin_bp  # make sure admin.py exists
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)

    return app
