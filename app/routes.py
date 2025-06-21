import os
import csv
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, make_response
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from .cv_parser import extract_cv_text, generate_cv_feedback
from .job_matcher import calculate_match_score, recommend_roles, update_feedback, load_feedback

main = Blueprint('main', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'docx'}
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 🔐 Dummy admin credentials (ideally store securely in a DB or .env)
ADMIN_CREDENTIALS = {
    "username": "admin",
    "password": generate_password_hash("admin123")
}

# ✅ Decorator to protect admin-only views
def admin_required(func):
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash("🔒 Please log in as admin.")
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)
    return wrapper

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@main.route('/match', methods=['POST'])
def match():
    if 'cv_file' not in request.files:
        flash('No file part')
        return redirect(url_for('main.index'))

    file = request.files['cv_file']
    job_description = request.form.get('job_description', '')
    job_title = request.form.get('job_title', '')

    if file.filename == '' or not job_description:
        flash('Please upload a CV and paste a job description.')
        return redirect(url_for('main.index'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        cv_text = extract_cv_text(file_path)
        match_score = calculate_match_score(cv_text, job_description)
        feedback_improve = generate_cv_feedback(cv_text, job_description)
        suggested_roles = recommend_roles(cv_text, job_description)

        session['cv_text'] = cv_text
        session['job_description'] = job_description
        session['match_score'] = match_score
        session['cv_feedback'] = feedback_improve
        session['suggested_roles'] = suggested_roles
        session['job_title'] = job_title

        return redirect(url_for('main.results'))

    flash('Invalid file type. Only PDF and DOCX are allowed.')
    return redirect(url_for('main.index'))

@main.route('/results', methods=['GET'])
def results():
    return render_template('index.html',
                           cv_text=session.get('cv_text'),
                           job_description=session.get('job_description'),
                           match_score=session.get('match_score'),
                           cv_feedback=session.get('cv_feedback'),
                           suggested_roles=session.get('suggested_roles'),
                           job_title=session.get('job_title'))

@main.route('/feedback', methods=['POST'])
def feedback():
    job_title = request.form.get('job_title', '').strip()
    actual_score = float(request.form.get('actual_score', 0))
    cv_text = session.get('cv_text', '')
    job_description = session.get('job_description', '')

    if job_title and cv_text and job_description:
        update_feedback(job_title, cv_text, job_description, actual_score)
        flash('✅ Thank you! Your feedback helps us improve matching accuracy.')
    else:
        flash('⚠️ Could not process feedback. Missing data.')

    return redirect(url_for('main.index'))

# ✅ Admin dashboard (protected)
@main.route('/dashboard', methods=['GET'])
@admin_required
def dashboard():
    # Load and filter feedback
    feedback_data = load_feedback()
    job_filter = request.args.get('job_title', '').strip().lower()
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    rating_filter = request.args.get('rating', '')

    filtered_data = []
    for entry in feedback_data:
        if not isinstance(entry, dict):  # ✅ Prevent .get() on strings
            continue

        matches = True

        if job_filter and job_filter not in entry.get("job_title", "").lower():
            matches = False

        if rating_filter and str(entry.get("rating", "")) != rating_filter:
            matches = False

        if start_date:
            try:
                if datetime.strptime(entry["timestamp"], "%Y-%m-%d %H:%M:%S") < datetime.strptime(start_date, "%Y-%m-%d"):
                    matches = False
            except Exception:
                pass

        if end_date:
            try:
                if datetime.strptime(entry["timestamp"], "%Y-%m-%d %H:%M:%S") > datetime.strptime(end_date, "%Y-%m-%d"):
                    matches = False
            except Exception:
                pass

        if matches:
            filtered_data.append(entry)

    # Analytics summary
    latest_score = session.get("match_score", 0)
    latest_job_title = session.get("job_title", "N/A")
    total_feedback = len(feedback_data)
    accuracy_gain = 12  # Placeholder
    avg_match_score = f"{round(sum(e.get('system_score', 0) for e in feedback_data if isinstance(e, dict)) / total_feedback, 2)}%" if total_feedback else "74%"

    return render_template("dashboard.html",
                           latest_match_score=latest_score,
                           latest_job_title=latest_job_title,
                           improvement_rate=accuracy_gain,
                           total_feedback=total_feedback,
                           feedback_log=filtered_data,
                           avg_match_score=avg_match_score,
                           total_users="N/A",
                           total_scans="N/A")

# ✅ Export Feedback as CSV (protected)
@main.route('/export-feedback', methods=['GET'])
@admin_required
def export_feedback():
    feedback = load_feedback()

    # Create CSV rows
    output = []
    headers = ["job_title", "actual_score", "system_score", "rating", "timestamp"]
    output.append(headers)

    for entry in feedback:
        if not isinstance(entry, dict):
            continue
        output.append([
            entry.get("job_title", ""),
            entry.get("actual_score", ""),
            entry.get("system_score", ""),
            entry.get("rating", ""),
            entry.get("timestamp", "")
        ])

    csv_data = "\n".join([",".join(map(str, row)) for row in output])
    response = make_response(csv_data)
    response.headers["Content-Disposition"] = "attachment; filename=feedback_data.csv"
    response.headers["Content-type"] = "text/csv"
    return response

# ✅ Logout route
@main.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    flash("✅ You have been logged out.")
    return redirect(url_for('auth.login'))

# ✅ Admin password change route
@main.route('/change-password', methods=['GET', 'POST'])
@admin_required
def change_password():
    if request.method == 'POST':
        current = request.form['current_password']
        new = request.form['new_password']
        confirm = request.form['confirm_password']

        if not check_password_hash(ADMIN_CREDENTIALS['password'], current):
            flash("❌ Current password is incorrect.", "danger")
        elif new != confirm:
            flash("⚠️ New passwords do not match.", "warning")
        else:
            ADMIN_CREDENTIALS['password'] = generate_password_hash(new)
            flash("✅ Password updated successfully.", "success")
            return redirect(url_for('main.dashboard'))

    return render_template('change_password.html')
