from flask import Flask, current_app
from flask_pymongo import PyMongo
from flask_login import LoginManager, current_user
from flask_principal import Principal, Permission, RoleNeed, identity_loaded, UserNeed
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect

mongo = PyMongo()
login_manager = LoginManager()
principals = Principal()
mail = Mail()
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per day", "50 per hour"], storage_uri="memory://")
csrf = CSRFProtect()

admin_permission = Permission(RoleNeed('admin'))

def create_app(config_name='default'):
    app = Flask(__name__, instance_relative_config=False)
    from config import config
    app.config.from_object(config[config_name])

    mongo.init_app(app)
    login_manager.init_app(app)
    principals.init_app(app)
    mail.init_app(app)
    limiter.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Molimo prijavite se za pristup ovoj stranici.'
    login_manager.login_message_category = 'warning'

    from app.models import User as UserModel

    @login_manager.user_loader
    def load_user(user_id):
        return UserModel.get_by_id(user_id)

    @identity_loaded.connect_via(app)
    def on_identity_loaded(sender, identity):
        identity.user = current_user
        if hasattr(current_user, 'id'):
            identity.provides.add(UserNeed(str(current_user.id)))
        if hasattr(current_user, 'role'):
            identity.provides.add(RoleNeed(current_user.role))

    # register blueprints
    from app.auth import auth_bp
    from app.main import main_bp
    from app.ads import ads_bp
    from app.admin import admin_bp
    from app.profile import profile_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(ads_bp, url_prefix='/ads')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(profile_bp, url_prefix='/profile')

    register_error_handlers(app)

    @app.after_request
    def set_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response

    with app.app_context():
        create_admin_user()

    @app.context_processor
    def inject_now():
        from datetime import datetime
        return {'current_year': datetime.utcnow().year}

    return app

def register_error_handlers(app):
    from flask import render_template
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404
    @app.errorhandler(429)
    def rate_limited(e):
        return render_template('errors/429.html'), 429
    @app.errorhandler(500)
    def internal_error(e):
        return render_template('errors/500.html'), 500

def create_admin_user():
    from app.models import User
    from flask import current_app
    admin_username = current_app.config.get('ADMIN_USERNAME')
    admin_email = current_app.config.get('ADMIN_EMAIL')
    admin_password_hash = current_app.config.get('ADMIN_PASSWORD_HASH')
    if not admin_username or not admin_password_hash:
        return
    existing = User.get_by_username(admin_username)
    if not existing:
        User.create_admin(admin_username, admin_email, admin_password_hash)
        print(f"Admin user '{admin_username}' created.")
