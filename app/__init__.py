from flask import Flask
from flask_session import Session
import os

def create_app():
    app = Flask(__name__)

    # ✅ Add a strong secret key
    app.secret_key = "your-very-secret-key"

    # ✅ Configure Flask-Session
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_USE_SIGNER'] = True
    app.config['SESSION_FILE_DIR'] = os.path.join(os.getcwd(), 'flask_session')

    # ✅ Initialize server-side session
    Session(app)

    # ✅ Register main blueprint (already done)
    from .routes import main
    app.register_blueprint(main)

    # ✅ Register the auth blueprint
    from .auth_routes import auth
    app.register_blueprint(auth)

    return app
