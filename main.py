from flask import Flask, request, render_template, send_file
from app.cv_parser import extract_text_from_file, extract_keywords
from app.brightermonday_scraper import scrape_brightermonday_jobs
import csv
import io
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['cv']
        if file:
            text = extract_text_from_file(file)
            keywords = extract_keywords(text, top_n=5)
            job_results = scrape_brightermonday_jobs(keywords)
            return render_template("results.html", jobs=job_results, keywords=keywords)
    return render_template("index.html")

# ✅ New Route: Export Feedback as CSV
@app.route('/export-feedback')
def export_feedback():
    feedback_file = os.path.join('data', 'feedback_log.csv')  # Adjust path as needed
    if not os.path.exists(feedback_file):
        return "⚠️ No feedback data available.", 404

    # Prepare CSV for download
    output = io.StringIO()
    with open(feedback_file, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        writer = csv.writer(output)
        for row in reader:
            writer.writerow(row)

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name='feedback_export.csv'
    )

if __name__ == "__main__":
    app.run(debug=True)
