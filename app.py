from flask import Flask, render_template, jsonify, Response
import psutil
import platform
import time
import csv
import os
from io import StringIO, BytesIO

app = Flask(__name__)

def get_system_data():
    try:
        cpu = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory().percent

        # ✅ FIXED FOR LINUX (Railway)
        try:
            disk = psutil.disk_usage('/').percent
        except:
            disk = 0

        os_name = platform.system()
        cores = psutil.cpu_count() or 0
        total_ram = round(psutil.virtual_memory().total / (1024**3), 2)

        uptime_seconds = time.time() - psutil.boot_time()
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)

        return {
            "cpu": cpu or 0,
            "ram": ram or 0,
            "disk": disk or 0,
            "os": os_name,
            "cores": cores,
            "total_ram": total_ram,
            "uptime": f"{uptime_hours}h {uptime_minutes}m"
        }

    except Exception as e:
        return {"error": str(e)}


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/data')
def data():
    return jsonify(get_system_data())


# 🔥 CSV DOWNLOAD (WORKING)
@app.route('/report/csv')
def download_csv():
    data = get_system_data()

    si = StringIO()
    writer = csv.writer(si)

    writer.writerow(["Metric", "Value"])
    for key, value in data.items():
        writer.writerow([key, value])

    return Response(
        si.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=report.csv"}
    )


# 🔥 PDF DOWNLOAD (FIXED - NO FILE SAVE)
@app.route('/report/pdf')
def download_pdf():
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.pagesizes import letter

    data = get_system_data()

    buffer = BytesIO()  # ✅ in-memory file
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    content = []
    content.append(Paragraph("System Monitoring Report", styles['Title']))
    content.append(Spacer(1, 10))

    for key, value in data.items():
        content.append(Paragraph(f"<b>{key.upper()}</b>: {value}", styles['Normal']))
        content.append(Spacer(1, 6))

    doc.build(content)

    buffer.seek(0)

    return Response(
        buffer,
        mimetype='application/pdf',
        headers={"Content-Disposition": "attachment; filename=report.pdf"}
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)