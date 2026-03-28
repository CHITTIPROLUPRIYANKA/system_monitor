from flask import Flask, render_template, jsonify, Response
import psutil
import platform
import time
import csv
import os
from io import StringIO

app = Flask(__name__)

def get_system_data():
    cpu = psutil.cpu_percent(interval=None)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('C:\\').percent

    os_name = platform.system()
    cores = psutil.cpu_count()
    total_ram = round(psutil.virtual_memory().total / (1024**3), 2)

    uptime_seconds = time.time() - psutil.boot_time()
    uptime_hours = int(uptime_seconds // 3600)
    uptime_minutes = int((uptime_seconds % 3600) // 60)

    return {
        "cpu": cpu,
        "ram": ram,
        "disk": disk,
        "os": os_name,
        "cores": cores,
        "total_ram": total_ram,
        "uptime": f"{uptime_hours}h {uptime_minutes}m"
    }

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/data')
def data():
    return jsonify(get_system_data())

# 🔥 CSV DOWNLOAD
@app.route('/report/csv')
def download_csv():
    data = get_system_data()

    si = StringIO()
    writer = csv.writer(si)

    writer.writerow(["Metric", "Value"])
    writer.writerow(["CPU (%)", data["cpu"]])
    writer.writerow(["RAM (%)", data["ram"]])
    writer.writerow(["Disk (%)", data["disk"]])
    writer.writerow(["OS", data["os"]])
    writer.writerow(["CPU Cores", data["cores"]])
    writer.writerow(["Total RAM (GB)", data["total_ram"]])
    writer.writerow(["Uptime", data["uptime"]])

    output = si.getvalue()

    return Response(output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=report.csv"})

# 🔥 PDF DOWNLOAD
@app.route('/report/pdf')
def download_pdf():
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors

    data = get_system_data()

    file_path = "report.pdf"
    doc = SimpleDocTemplate(file_path, pagesize=letter)
    styles = getSampleStyleSheet()

    content = []

    content.append(Paragraph("System Monitoring Report", styles['Title']))
    content.append(Spacer(1, 10))

    for key, value in data.items():
        content.append(Paragraph(f"<b>{key.upper()}</b>: {value}", styles['Normal']))
        content.append(Spacer(1, 6))

    doc.build(content)

    with open(file_path, "rb") as f:
        pdf = f.read()

    return Response(pdf,
        mimetype='application/pdf',
        headers={"Content-Disposition": "attachment;filename=report.pdf"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)