from flask import Flask, render_template, request, jsonify, send_file
from pdf2docx import Converter
import os
import uuid
import time  # Simulates processing delay

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

tasks = {}  # To track task statuses

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/convert', methods=['POST'])
def convert_pdf_to_word():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if file:
        # Generate unique task ID
        task_id = str(uuid.uuid4())

        # Save the uploaded PDF
        pdf_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(pdf_path)

        # Initialize task
        tasks[task_id] = {"status": "processing", "file": None}

        # Simulate background processing (replace with actual processing)
        def process_task():
            word_path = pdf_path.replace(".pdf", ".docx")
            cv = Converter(pdf_path)
            time.sleep(5)  # Simulate delay for conversion
            cv.convert(word_path, start=0, end=None)
            cv.close()
            tasks[task_id] = {"status": "ready", "file": os.path.basename(word_path)}

        # Start task processing
        import threading
        threading.Thread(target=process_task).start()

        return jsonify({"task_id": task_id})

@app.route('/status', methods=['GET'])
def check_status():
    task_id = request.args.get("task_id")
    if task_id in tasks:
        return jsonify(tasks[task_id])
    return jsonify({"status": "not_found"}), 404

@app.route('/download', methods=['GET'])
def download_file():
    file_name = request.args.get("file")
    file_path = os.path.join(UPLOAD_FOLDER, file_name)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return "File not found", 404

if __name__ == '__main__':
    app.run()
