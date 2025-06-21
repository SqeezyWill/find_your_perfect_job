import os
import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash, generate_password_hash

auth = Blueprint('auth', __name__)

# Config file to store hashed password
CONFIG_FILE = "admin_config.json"

# Load admin credentials
def load_credentials():
    if not os.path.exists(CONFIG_FILE):
        return {"username": "admin", "password_hash": generate_password_hash("phantom1234")}
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

# Save updated password hash
def save_credentials(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f)

credentials = load_credentials()
ADMIN_USERNAME = credentials["username"]
ADMIN_PASSWORD_HASH = credentials["password_hash"]

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
            session['admin_logged_in'] = True
            flash("✅ Login successful.")
            return redirect(url_for('main.dashboard'))
        else:
            flash("❌ Invalid username or password.")
            return redirect(url_for('auth.login'))

    return render_template('login.html')


# ✅ Route to change password
@auth.route('/change-password', methods=['GET', 'POST'])
def change_password():
    if not session.get('admin_logged_in'):
        flash("🔒 You must be logged in to change password.")
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        current = request.form.get('current_password', '').strip()
        new = request.form.get('new_password', '').strip()
        confirm = request.form.get('confirm_password', '').strip()

        if not check_password_hash(credentials["password_hash"], current):
            flash("❌ Current password is incorrect.")
            return redirect(url_for('auth.change_password'))

        if new != confirm:
            flash("❌ New passwords do not match.")
            return redirect(url_for('auth.change_password'))

        if len(new) < 8:
            flash("❌ Password must be at least 8 characters.")
            return redirect(url_for('auth.change_password'))

        # Save new password
        new_hash = generate_password_hash(new)
        credentials["password_hash"] = new_hash
        save_credentials(credentials)

        flash("✅ Password changed successfully.")
        return redirect(url_for('main.dashboard'))

    return render_template("change_password.html")
