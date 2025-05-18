import os
from flask import Flask, request, render_template, send_file, url_for
import pandas as pd
from ydata_profiling import ProfileReport
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
REPORT_FOLDER = "reports"
ALLOWED_EXTENSIONS = {'csv'}

# Giới hạn kích thước file upload tối đa 10MB
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10 MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('upload.html', error="Không tìm thấy file trong request.")
        file = request.files['file']
        if file.filename == '':
            return render_template('upload.html', error="Bạn chưa chọn file.")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            try:
                data = pd.read_csv(filepath)
                profile = ProfileReport(data, title="Pandas Profiling Report EMR")
                html_report = os.path.join(REPORT_FOLDER, 'report_emr.html')
                profile.to_file(output_file=html_report)
            except Exception as e:
                return render_template('upload.html', error=f"Lỗi xử lý file: {e}")

            return render_template('result.html', report_url=url_for('download_report'))
        else:
            return render_template('upload.html', error="Chỉ cho phép file CSV.")
    return render_template('upload.html')

@app.route('/download')
def download_report():
    html_report = os.path.join(REPORT_FOLDER, 'report_emr.html')
    if not os.path.exists(html_report):
        return "Báo cáo chưa được tạo, vui lòng upload file để tạo báo cáo."
    return send_file(html_report, as_attachment=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
