from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from os import path, getenv
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
import json
import time
from sqlalchemy.exc import OperationalError
from sqlalchemy import text



app_config = None

with open('config.json', 'r') as config_file:
    app_config = json.load(config_file)

db = SQLAlchemy()
migrate = Migrate()

def create_app(env='development'):
    app = Flask(__name__)
    csrf = CSRFProtect(app)
    app.config['SECRET_KEY'] = getenv('SECRET_KEY', app_config[env]['SECRET_KEY'])
    app.config['SQLALCHEMY_DATABASE_URI'] = getenv('DATABASE_URI', app_config[env]['DATABASE_URI'])
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Turn off tracking modifications
    db.init_app(app)
    migrate.init_app(app, db)

    # Import models here to avoid circular import
    from .models import GPU, Price, Users, Subscriptions
    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    max_retries = 10  # You can adjust this number as needed
    retries = 0

    while retries < max_retries:
        try:
            with app.app_context():
                # Directly query the information schema to check for table existence
                query = text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'gpu')")
                result = db.session.execute(query)
                table_exists = result.scalar()

                if not table_exists:
                    print("Database tables not found. Initializing...")
                    db.create_all()
                else:
                    print("Database tables already exist.")

            break  # Break out of the loop if database setup succeeds
        except OperationalError:
            print(f"Database connection failed. Retrying in 5 seconds ({retries}/{max_retries})")
            time.sleep(5)
            retries += 1
    else:
        print("Failed to establish database connection after multiple retries. Exiting.")
        return None  # Return None to indicate failure

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return Users.query.get(int(id))
    
    return app
