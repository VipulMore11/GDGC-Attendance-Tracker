from flask import Flask, request, jsonify, render_template, redirect, url_for
from email_service import process_csv_and_send_emails
from qr_code_service import record_attendance
import os

app = Flask(__name__)
app.config.from_object('config.Config')

@app.route('/')
def home():
    return "Welcome to the Event Management Service!"

@app.route('/send-emails', methods=['POST'])
def send_emails():
    try:
        csv_file_path = app.config['CSV_FILE_PATH']
        log_file_path = app.config['LOG_FILE_PATH']
        event_details = app.config['EVENT_DETAILS']

        process_csv_and_send_emails(csv_file_path, event_details, log_file_path)
        return jsonify({"message": "Emails processed successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/record-attendance', methods=['POST'])
def attendance():
    try:
        ticket_id = request.json.get('ticket_id')
        if not ticket_id:
            return jsonify({"error": "Ticket ID is required"}), 400

        attendance_recorded = record_attendance(ticket_id)
        if attendance_recorded:
            return jsonify({"message": "Attendance recorded successfully"}), 200
        else:
            return jsonify({"error": "Ticket not found or already marked"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)