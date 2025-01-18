class Config:
    CSV_FILE_PATH = 'registration_details.csv'
    LOG_FILE_PATH = 'logs/email_log.csv'
    EVENT_DETAILS = {
        'name': 'Pixel Designathon: Cause every pixel counts...',
        'start_date': '20-01-2025',
        'end_date': '23-01-2025',
        'venue': 'Online',
    }
    SQLALCHEMY_DATABASE_URI = 'sqlite:///event_management.db'  # SQLite database
    SQLALCHEMY_TRACK_MODIFICATIONS = False