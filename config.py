import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'job-portal-secret-key-2024'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Resume scoring weights
    RESUME_WEIGHTS = {
        'skills_match': 0.35,
        'experience_match': 0.25,
        'education_match': 0.15,
        'keywords_match': 0.15,
        'format_score': 0.10
    }
    
    # Minimum score for auto-approval
    AUTO_APPROVE_THRESHOLD = 70
    AUTO_REJECT_THRESHOLD = 40
