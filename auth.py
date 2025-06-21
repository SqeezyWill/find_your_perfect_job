# app/auth.py

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint('auth', __name__)

# ✅ Use a fixed hash instead of regenerating it every time the app reloads
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD_HASH = "scrypt:32768:8:1$XMIFPKw4jJzaRfmL$34ef32be9776c8f4ada01d6a224d414185c114887bcc020459f42ef591a5f3b66217fc87db961ead3d99bc4cbbaeb5be86e501c3aeaa66496e0c7366efff8f2a"

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
            session['admin_logged_in'] = True
            session['user_name'] = username
            flash("✅ Login successful.")
            return redirect(url_for('main.dashboard'))
        else:
            flash("❌ Invalid username or password.")
            return redirect(url_for('auth.login'))

    return render_template('login.html')

@auth.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    session.pop('user_name', None)
    flash("✅ You have been logged out.")
    return redirect(url_for('auth.login'))

@auth.route('/change-password', methods=['GET', 'POST'])
def change_password():
    global ADMIN_PASSWORD_HASH
    if not session.get('admin_logged_in'):
        flash("🔒 Please log in to change password.")
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        current = request.form['current_password']
        new = request.form['new_password']

        if check_password_hash(ADMIN_PASSWORD_HASH, current):
            ADMIN_PASSWORD_HASH = generate_password_hash(new)
            flash("✅ Password updated successfully.")
            return redirect(url_for('main.dashboard'))
        else:
            flash("❌ Current password is incorrect.")

    return render_template('change_password.html')
