# Models module - all database models
from extensions import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'seeker' or 'employer'
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    headline = db.Column(db.String(200))
    bio = db.Column(db.Text)
    profile_image = db.Column(db.String(200))
    face_encoding = db.Column(db.Text)  # JSON encoded face data
    company_name = db.Column(db.String(100))  # For employers
    preferred_language = db.Column(db.String(10), default='en')  # 'en', 'hi', 'ta'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    skills = db.relationship('Skill', backref='user', lazy=True, cascade='all, delete-orphan')
    experiences = db.relationship('Experience', backref='user', lazy=True, cascade='all, delete-orphan')
    educations = db.relationship('Education', backref='user', lazy=True, cascade='all, delete-orphan')
    resume = db.relationship('Resume', backref='user', uselist=False, cascade='all, delete-orphan')
    posts = db.relationship('Post', backref='author', lazy=True, cascade='all, delete-orphan')
    jobs = db.relationship('Job', backref='employer', lazy=True, cascade='all, delete-orphan')
    applications = db.relationship('Application', backref='applicant', lazy=True, cascade='all, delete-orphan')
    
    # New relationships
    test_results = db.relationship('PsychologicalTestResult', backref='user', lazy=True)
    skill_test_results = db.relationship('SkillTestResult', backref='user', lazy=True)
    event_registrations = db.relationship('EventRegistration', backref='user', lazy=True)
    certificates = db.relationship('Certificate', backref='user', lazy=True)

class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50))  # 'technical', 'soft', 'tool'
    endorsements = db.Column(db.Integer, default=0)

class Experience(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    is_current = db.Column(db.Boolean, default=False)
    description = db.Column(db.Text)

class Education(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    degree = db.Column(db.String(100), nullable=False)
    institution = db.Column(db.String(150), nullable=False)
    field = db.Column(db.String(100))
    year = db.Column(db.Integer)
    grade = db.Column(db.String(20))

class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    file_path = db.Column(db.String(200))
    ats_score = db.Column(db.Integer, default=0)
    skills_extracted = db.Column(db.Text)  # JSON
    keywords = db.Column(db.Text)  # JSON
    parsed_data = db.Column(db.Text)  # JSON
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text)  # JSON list of requirements
    skills_required = db.Column(db.Text)  # JSON list of skills
    experience_min = db.Column(db.Integer, default=0)
    experience_max = db.Column(db.Integer)
    salary_min = db.Column(db.Integer)
    salary_max = db.Column(db.Integer)
    location = db.Column(db.String(100))
    job_type = db.Column(db.String(50))  # 'full-time', 'part-time', 'contract', 'remote'
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    applications = db.relationship('Application', backref='job', lazy=True, cascade='all, delete-orphan')

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'approved', 'rejected', 'under_review'
    ai_score = db.Column(db.Integer)
    match_percentage = db.Column(db.Integer)
    skills_match = db.Column(db.Text)  # JSON
    missing_skills = db.Column(db.Text)  # JSON
    feedback = db.Column(db.Text)  # JSON with AI feedback
    letter_path = db.Column(db.String(200))
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    decided_at = db.Column(db.DateTime)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    post_type = db.Column(db.String(20), default='text')  # 'text', 'job_update', 'achievement'
    image_url = db.Column(db.String(200))
    likes_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    comments = db.relationship('Comment', backref='post', lazy=True, cascade='all, delete-orphan')
    likes = db.relationship('Like', backref='post', lazy=True, cascade='all, delete-orphan')

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='comments')

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Connection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    connected_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'accepted', 'rejected'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Endorsement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    skill_id = db.Column(db.Integer, db.ForeignKey('skill.id'), nullable=False)
    endorsed_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ==================== NEW MODELS ====================

class PsychologicalTest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    questions_json = db.Column(db.Text, nullable=False)  # JSON list of questions
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PsychologicalTestResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    test_id = db.Column(db.Integer, db.ForeignKey('psychological_test.id'), nullable=False)
    score = db.Column(db.Integer)
    analysis = db.Column(db.Text)  # Detailed analysis text
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)

class SkillTest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    skill_name = db.Column(db.String(50), nullable=False)
    level = db.Column(db.String(20))  # 'beginner', 'intermediate', 'advanced'
    questions_json = db.Column(db.Text, nullable=False)
    duration_minutes = db.Column(db.Integer, default=30)

class SkillTestResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    test_id = db.Column(db.Integer, db.ForeignKey('skill_test.id'), nullable=False)
    score = db.Column(db.Integer)
    is_passed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    organizer = db.Column(db.String(100))
    description = db.Column(db.Text)
    event_type = db.Column(db.String(50))  # 'workshop', 'webinar', 'conference', 'internship_fair'
    is_internship = db.Column(db.Boolean, default=False)
    location = db.Column(db.String(200))  # 'Online' or city name
    url = db.Column(db.String(500))
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    image_url = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class EventRegistration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)

class Certificate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    cert_type = db.Column(db.String(50))  # 'psychology', 'skill'
    reference_id = db.Column(db.Integer)  # ID of the test result
    title = db.Column(db.String(200))
    file_path = db.Column(db.String(200))
    issued_at = db.Column(db.DateTime, default=datetime.utcnow)
