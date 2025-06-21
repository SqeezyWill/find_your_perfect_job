from app import create_app
import os

# ✅ Ensure session directory exists for Flask-Session
os.makedirs("flask_session", exist_ok=True)

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
