from functools import wraps
from flask import abort
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(403)
        if current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated

def owner_or_admin_required(model_class, id_param='id'):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(403)
            item_id = kwargs.get(id_param)
            item = model_class.get_by_id(item_id)
            if not item:
                abort(404)
            if current_user.role != 'admin' and item.user_id != current_user.id:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator
