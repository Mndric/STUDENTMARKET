import os
import sys
import importlib.util

try:
    from app import create_app
except ImportError:
    spec = importlib.util.spec_from_file_location(
        "app",
        os.path.join(os.path.dirname(__file__), "app", "__init__.py")
    )
    app_module = importlib.util.module_from_spec(spec)
    sys.modules["app"] = app_module
    spec.loader.exec_module(app_module)
    from app import create_app

env = os.environ.get('FLASK_ENV', 'development')
app = create_app(env)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
