from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    ticket_id = db.Column(db.String(50), unique=True, nullable=False)
    qr_code = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<User {self.name} - {self.email}>"
    
class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('attendances', lazy=True))
    event_name = db.Column(db.String(100), nullable=False)
    attended_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Attendance for {self.user.name} at {self.event_name}>"