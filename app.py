import os
from flask import Flask, request, render_template, send_file, redirect, url_for
import pandas as pd
from ydata_profiling import ProfileReport
from werkzeug.utils import secure_filename

app = Flask(__name__)
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

            data = pd.read_csv(filepath)
            profile = ProfileReport(data, title="Pandas Profiling Report EMR")
            html_report = os.path.join(REPORT_FOLDER, 'report_emr.html')
            profile.to_file(output_file=html_report)

            return render_template('result.html', report_url=url_for('download_report'))
        else:
            return render_template('upload.html', error="Allowed file type: csv")
    return render_template('upload.html')

@app.route('/download')
def download_report():
    html_report = os.path.join(REPORT_FOLDER, 'report_emr.html')
    return send_file(html_report, as_attachment=True)

import os
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
