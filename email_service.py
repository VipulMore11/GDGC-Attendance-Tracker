import os
import smtplib
import csv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from io import BytesIO
from xhtml2pdf import pisa
from jinja2 import Template
import pandas as pd
from datetime import datetime
from models import db, User
from qr_code_service import generate_qr_code

def load_template(template_name):
    with open(template_name, 'r', encoding='utf-8') as file:
        return file.read()

def generate_pdf(ticket_content):
    pdf_buffer = BytesIO()
    pisa_status = pisa.CreatePDF(ticket_content, dest=pdf_buffer)
    pdf_buffer.seek(0)
    if pisa_status.err:
        raise Exception("Error generating PDF")
    return pdf_buffer

def send_email(subject, recipient_email, html_body, pdf_name, pdf_buffer):
    sender_email = "helpingh861@gmail.com"
    sender_password = "cxea kfhb jjjz ouyb"
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = recipient_email

    message.attach(MIMEText(html_body, "html"))

    pdf_attachment = MIMEApplication(pdf_buffer.read(), _subtype="pdf")
    pdf_attachment.add_header(
        "Content-Disposition",
        f"attachment; filename={pdf_name}",
    )
    message.attach(pdf_attachment)

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, message.as_string())

def process_csv_and_send_emails(csv_file_path, event_details, log_file_path):
    df = pd.read_csv(csv_file_path)

    if not os.path.exists(log_file_path):
        with open(log_file_path, 'w', newline='') as log_file:
            writer = csv.writer(log_file)
            writer.writerow(["Name", "Email", "Time"])

    processed_emails = set()
    with open(log_file_path, 'r') as log_file:
        reader = csv.DictReader(log_file)
        for row in reader:
            processed_emails.add(row["Email"])

    for index, row in df.iterrows():
        first_name = row['Name']
        email = row['Email']

        if email in processed_emails:
            print(f"Skipping {email}: Email already sent.")
            continue

        event_name = event_details['name']
        start_date = event_details['start_date']
        end_date = event_details['end_date']
        venue_name = event_details['venue']

        ticket_id = f"TKT-{datetime.now().strftime('%Y%m%d')}-{index+1:04d}"
        qr_data = (
            f"Ticket ID: {ticket_id}\n"
            f"Name: {first_name}\n"
            f"Email: {email}\n"
            f"Event: {event_name}\n"
            f"Date: {start_date} to {end_date}\n"
            f"Venue: {venue_name}"
        )

        qr_code_image = generate_qr_code(qr_data)

        email_template_path = "templates/email_template.html"
        ticket_template_path = "templates/ticket_template.html"
        email_template = load_template(email_template_path)
        ticket_template = load_template(ticket_template_path)

        email_html = Template(email_template).render(
            first_name=first_name,
            event_name=event_name,
            start_date=start_date,
            end_date=end_date,
            venue_name=venue_name,
        )
        ticket_html = Template(ticket_template).render(
            first_name=first_name,
            event_name=event_name,
            start_date=start_date,
            end_date=end_date,
            venue_name=venue_name,
            ticket_id=ticket_id,
            qr_code=qr_code_image
        )

        pdf_buffer = generate_pdf(ticket_html)

        try:
            send_email(
                subject=f"Registration Confirmation for {event_name}",
                recipient_email=email,
                html_body=email_html,
                pdf_name=f"{event_name}_Ticket_{ticket_id}.pdf",
                pdf_buffer=pdf_buffer,
            )
            print(f"Email sent successfully to {email}")

            with open(log_file_path, 'a', newline='') as log_file:
                writer = csv.writer(log_file)
                writer.writerow([first_name, email, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
            user = User(
            name=first_name,
            email=email,
            ticket_id=ticket_id,
            qr_code=qr_code_image
            )
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            print(f"Failed to send email to {email}: {str(e)}")
        finally:
            pdf_buffer.close()
