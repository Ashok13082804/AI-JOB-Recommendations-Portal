from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_file
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import json

from config import Config
from extensions import db, login_manager
from models import User, Skill, Experience, Education, Resume, Job, Application, Post, Comment, Like, Connection, Endorsement

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions with app
db.init_app(app)
login_manager.init_app(app)

# Ensure upload directories exist
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'resumes'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'profiles'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'letters'), exist_ok=True)

# Custom Jinja2 filter for JSON parsing
def from_json(value):
    if not value:
        return []
    try:
        return json.loads(value)
    except:
        return []

app.jinja_env.filters['from_json'] = from_json

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

# ==================== ROUTES ====================

@app.route('/')
def index():
    featured_jobs = Job.query.filter_by(is_active=True).order_by(Job.created_at.desc()).limit(6).all()
    return render_template('index.html', featured_jobs=featured_jobs)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        if User.query.filter_by(email=data.get('email')).first():
            return jsonify({'success': False, 'message': 'Email already registered'})
        
        user = User(
            email=data.get('email'),
            password_hash=generate_password_hash(data.get('password')),
            name=data.get('name'),
            phone=data.get('phone'),
            role=data.get('role', 'seeker'),
            headline=data.get('headline'),
            bio=data.get('bio'),
            company_name=data.get('company_name') if data.get('role') == 'employer' else None
        )
        
        # Handle face encoding
        if data.get('face_encoding'):
            user.face_encoding = json.dumps(data.get('face_encoding'))
        
        db.session.add(user)
        db.session.commit()
        
        # Handle skills if provided
        if data.get('skills'):
            skills = data.get('skills').split(',') if isinstance(data.get('skills'), str) else data.get('skills')
            for skill_name in skills:
                skill = Skill(user_id=user.id, name=skill_name.strip(), category='technical')
                db.session.add(skill)
            db.session.commit()
        
        login_user(user)
        return jsonify({'success': True, 'redirect': url_for('dashboard')})
    
    return render_template('auth/register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        user = User.query.filter_by(email=data.get('email')).first()
        
        if user and check_password_hash(user.password_hash, data.get('password')):
            login_user(user)
            return jsonify({'success': True, 'redirect': url_for('dashboard')})
        
        return jsonify({'success': False, 'message': 'Invalid email or password'})
    
    return render_template('auth/login.html')

@app.route('/login/face', methods=['POST'])
def face_login():
    data = request.get_json()
    email = data.get('email')
    face_data = data.get('face_encoding')
    
    user = User.query.filter_by(email=email).first()
    
    if not user or not user.face_encoding:
        return jsonify({'success': False, 'message': 'User not found or face not registered'})
    
    # Simple comparison - in production, use proper face matching
    stored_face = json.loads(user.face_encoding)
    
    # For demo: just check if face data was provided
    if face_data:
        login_user(user)
        return jsonify({'success': True, 'redirect': url_for('dashboard')})
    
    return jsonify({'success': False, 'message': 'Face verification failed'})

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'employer':
        jobs = Job.query.filter_by(employer_id=current_user.id).all()
        applications = Application.query.join(Job).filter(Job.employer_id == current_user.id).all()
        return render_template('dashboard/employer.html', jobs=jobs, applications=applications)
    else:
        applications = Application.query.filter_by(user_id=current_user.id).all()
        recommended_jobs = Job.query.filter_by(is_active=True).limit(5).all()
        return render_template('dashboard/seeker.html', applications=applications, recommended_jobs=recommended_jobs)

@app.route('/profile')
@app.route('/profile/<int:user_id>')
def profile(user_id=None):
    if user_id:
        user = User.query.get_or_404(user_id)
    elif current_user.is_authenticated:
        user = current_user
    else:
        return redirect(url_for('login'))
    
    posts = Post.query.filter_by(user_id=user.id).order_by(Post.created_at.desc()).limit(10).all()
    return render_template('profile/view.html', user=user, posts=posts)

@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        data = request.form
        
        current_user.name = data.get('name', current_user.name)
        current_user.headline = data.get('headline', current_user.headline)
        current_user.bio = data.get('bio', current_user.bio)
        current_user.phone = data.get('phone', current_user.phone)
        
        # Handle profile image upload
        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file and file.filename:
                filename = secure_filename(f"{current_user.id}_{file.filename}")
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'profiles', filename)
                file.save(file_path)
                current_user.profile_image = f"/static/uploads/profiles/{filename}"
        
        db.session.commit()
        return redirect(url_for('profile'))
    
    return render_template('profile/edit.html')

@app.route('/profile/skills', methods=['POST'])
@login_required
def update_skills():
    data = request.get_json()
    
    # Clear existing skills and add new ones
    Skill.query.filter_by(user_id=current_user.id).delete()
    
    for skill_data in data.get('skills', []):
        skill = Skill(
            user_id=current_user.id,
            name=skill_data.get('name'),
            category=skill_data.get('category', 'technical')
        )
        db.session.add(skill)
    
    db.session.commit()
    return jsonify({'success': True})

@app.route('/profile/experience', methods=['POST'])
@login_required
def add_experience():
    data = request.get_json()
    
    exp = Experience(
        user_id=current_user.id,
        title=data.get('title'),
        company=data.get('company'),
        location=data.get('location'),
        start_date=datetime.strptime(data.get('start_date'), '%Y-%m-%d') if data.get('start_date') else None,
        end_date=datetime.strptime(data.get('end_date'), '%Y-%m-%d') if data.get('end_date') else None,
        is_current=data.get('is_current', False),
        description=data.get('description')
    )
    
    db.session.add(exp)
    db.session.commit()
    return jsonify({'success': True, 'id': exp.id})

@app.route('/profile/education', methods=['POST'])
@login_required
def add_education():
    data = request.get_json()
    
    edu = Education(
        user_id=current_user.id,
        degree=data.get('degree'),
        institution=data.get('institution'),
        field=data.get('field'),
        year=data.get('year'),
        grade=data.get('grade')
    )
    
    db.session.add(edu)
    db.session.commit()
    return jsonify({'success': True, 'id': edu.id})

@app.route('/resume/analyze')
@login_required
def resume_analyze():
    return render_template('profile/analyze.html')

# Import and register blueprint routes
from modules.jobs import jobs_bp
from modules.resume_ai import resume_bp
from modules.social import social_bp

app.register_blueprint(jobs_bp)
app.register_blueprint(resume_bp)
app.register_blueprint(social_bp)

# ==================== MAIN ====================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
