from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask import Flask, request, jsonify, render_template, redirect, url_for
from email_service import process_csv_and_send_emails
from qr_code_service import record_attendance
import os
from models import db, User, Attendance

app = Flask(__name__, static_url_path='/static')
app.config.from_object(Config)

db.init_app(app)

# Manually create tables when the app starts
with app.app_context():
    db.create_all()

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
        event_name = request.json.get('event_name')  # Get event name from the request
        
        if not ticket_id or not event_name:
            return jsonify({"error": "Ticket ID and event name are required"}), 400

        user = User.query.filter_by(ticket_id=ticket_id).first()
        if user:
            # Create a new attendance record
            attendance_record = Attendance(user_id=user.id, event_name=event_name)
            db.session.add(attendance_record)
            db.session.commit()
            
            return jsonify({"message": f"Attendance recorded for {user.name} at {event_name}"}), 200
        else:
            return jsonify({"error": "Invalid Ticket ID"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/qr-scanner')
def qr_scanner():
    return render_template('qr_scanner.html')

if __name__ == '__main__':
    app.run(debug=True)