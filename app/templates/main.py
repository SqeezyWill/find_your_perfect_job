import csv
from flask import make_response, request
from datetime import datetime

@main.route('/export-feedback')
@admin_required
def export_feedback():
    from .job_matcher import load_feedback
    feedback_data = load_feedback()

    # Get filters from query parameters
    job_title_filter = request.args.get('job_title', '').lower()
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    rating_filter = request.args.get('rating', '')

    def is_match(entry):
        # Match job title filter
        if job_title_filter and job_title_filter not in entry.get('job_title', '').lower():
            return False

        # Match rating
        if rating_filter and str(entry.get('rating', '')) != rating_filter:
            return False

        # Match date range
        try:
            entry_date = datetime.strptime(entry.get('timestamp', '')[:10], '%Y-%m-%d')
            if start_date:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                if entry_date < start_dt:
                    return False
            if end_date:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                if entry_date > end_dt:
                    return False
        except Exception:
            pass

        return True

    # Apply filters
    filtered_data = [entry for entry in feedback_data if is_match(entry)]

    # Create CSV response
    output = csv.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Job Title", "Submitted Score", "System Score", "Rating", "Timestamp"])

    for entry in filtered_data:
        writer.writerow([
            entry.get("job_title", ""),
            entry.get("actual_score", ""),
            entry.get("system_score", ""),
            entry.get("rating", ""),
            entry.get("timestamp", "")
        ])

    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=filtered_feedback_log.csv"
    response.headers["Content-type"] = "text/csv"
    return response
