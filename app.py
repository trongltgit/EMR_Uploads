import os
import time
from flask import Flask, request, render_template, send_file, session, redirect, url_for
import pandas as pd
from ydata_profiling import ProfileReport
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # cần để dùng session
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # Giới hạn file 2MB

UPLOAD_FOLDER = "uploads"
REPORT_FOLDER = "reports"
ALLOWED_EXTENSIONS = {'csv'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('upload.html', error="No file part")
        file = request.files['file']
        if file.filename == '':
            return render_template('upload.html', error="No selected file")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            app.logger.info(f"File saved to {filepath}")
            try:
                data = pd.read_csv(filepath)
            except Exception as e:
                return render_template('upload.html', error=f"Error reading CSV: {e}")

            app.logger.info(f"Starting profile report generation...")
            timestamp = int(time.time())
            html_report = os.path.join(REPORT_FOLDER, f'report_emr_{timestamp}.html')
            profile = ProfileReport(data, title="Pandas Profiling Report EMR", minimal=True)
            profile.to_file(output_file=html_report)

            session['report_file'] = html_report

            return redirect(url_for('result'))
        else:
            return render_template('upload.html', error="Allowed file type: csv")
    return render_template('upload.html')

@app.route('/result')
def result():
    if 'report_file' not in session:
        return redirect(url_for('upload_file'))
    report_url = url_for('download_report')
    return render_template('result.html', report_url=report_url)

@app.route('/download')
def download_report():
    html_report = session.get('report_file', None)
    if html_report and os.path.exists(html_report):
        return send_file(html_report, as_attachment=True)
    return "Report not found", 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
