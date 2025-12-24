from flask import Blueprint, render_template, request, jsonify, redirect, url_for, current_app
from flask_login import login_required, current_user
from datetime import datetime
import json
import os

from extensions import db
from models import Job, Application, User, Resume, Skill

jobs_bp = Blueprint('jobs_bp', __name__, url_prefix='/jobs')

def get_user_skills(user):
    """Get user skills as lowercase list"""
    return [s.name.lower() for s in Skill.query.filter_by(user_id=user.id).all()]

def calculate_job_match(job, user_skills):
    """Calculate match percentage between job and user skills"""
    job_skills = []
    if job.skills_required:
        try:
            job_skills = json.loads(job.skills_required)
        except:
            job_skills = [s.strip() for s in job.skills_required.split(',')]
    
    job_skills_lower = set([s.lower() for s in job_skills])
    user_skills_set = set(user_skills)
    
    if not job_skills_lower:
        return 50  # Default if no skills specified
    
    matched = job_skills_lower.intersection(user_skills_set)
    return int((len(matched) / len(job_skills_lower)) * 100)

@jobs_bp.route('/')
def jobs_list():
    # Get filter parameters
    search = request.args.get('search', '')
    location = request.args.get('location', '')
    job_type = request.args.get('job_type', '')
    experience = request.args.get('experience', '')
    
    # Build query
    query = Job.query.filter_by(is_active=True)
    
    if search:
        # Enhanced search - also search in skills
        search_term = f'%{search}%'
        query = query.filter(
            (Job.title.ilike(search_term)) | 
            (Job.company.ilike(search_term)) |
            (Job.description.ilike(search_term)) |
            (Job.skills_required.ilike(search_term))
        )
    
    if location:
        query = query.filter(Job.location.ilike(f'%{location}%'))
    
    if job_type:
        if job_type == 'internship':
            query = query.filter((Job.job_type == 'internship') | (Job.title.ilike('%intern%')))
        else:
            query = query.filter(Job.job_type == job_type)
    
    if experience:
        exp_val = int(experience) if experience.isdigit() else 0
        query = query.filter(Job.experience_min <= exp_val)
    
    jobs_list = query.order_by(Job.created_at.desc()).all()
    
    # Calculate match percentage for logged-in users
    if current_user.is_authenticated and current_user.role == 'seeker':
        user_skills = get_user_skills(current_user)
        jobs_with_match = []
        for job in jobs_list:
            job.match_score = calculate_job_match(job, user_skills)
            jobs_with_match.append(job)
        
        # Sort by match score if user has skills
        if user_skills:
            jobs_with_match.sort(key=lambda x: x.match_score, reverse=True)
        jobs_list = jobs_with_match
    
    return render_template('jobs/list.html', 
                          jobs=jobs_list, 
                          search=search, 
                          location=location, 
                          job_type=job_type)

@jobs_bp.route('/search')
def search_jobs():
    """API endpoint for job search with AI recommendations"""
    search = request.args.get('q', '')
    location = request.args.get('location', '')
    
    query = Job.query.filter_by(is_active=True)
    
    if search:
        search_term = f'%{search}%'
        query = query.filter(
            (Job.title.ilike(search_term)) | 
            (Job.company.ilike(search_term)) |
            (Job.description.ilike(search_term)) |
            (Job.skills_required.ilike(search_term))
        )
    
    if location:
        query = query.filter(Job.location.ilike(f'%{location}%'))
    
    jobs = query.order_by(Job.created_at.desc()).limit(20).all()
    
    results = []
    user_skills = []
    if current_user.is_authenticated and current_user.role == 'seeker':
        user_skills = get_user_skills(current_user)
    
    for job in jobs:
        match_score = calculate_job_match(job, user_skills) if user_skills else 0
        skills = json.loads(job.skills_required) if job.skills_required else []
        
        results.append({
            'id': job.id,
            'title': job.title,
            'company': job.company,
            'location': job.location or 'Remote',
            'job_type': job.job_type or 'Full-time',
            'salary_min': job.salary_min,
            'salary_max': job.salary_max,
            'experience_min': job.experience_min,
            'experience_max': job.experience_max,
            'skills': skills[:5],
            'match_score': match_score,
            'description_snippet': job.description[:150] + '...' if len(job.description or '') > 150 else job.description
        })
    
    # Sort by match score if user is logged in
    if user_skills:
        results.sort(key=lambda x: x['match_score'], reverse=True)
    
    return jsonify({
        'success': True,
        'count': len(results),
        'jobs': results
    })

@jobs_bp.route('/recommendations')
@login_required
def get_recommendations():
    """Get AI-powered job recommendations based on user profile"""
    if current_user.role != 'seeker':
        return jsonify({'success': False, 'message': 'Only for job seekers'})
    
    user_skills = get_user_skills(current_user)
    
    # Get all active jobs
    all_jobs = Job.query.filter_by(is_active=True).all()
    
    # Score each job
    scored_jobs = []
    for job in all_jobs:
        match_score = calculate_job_match(job, user_skills)
        
        # Check experience match
        user_exp = 3  # Default, would be calculated from user's experience
        exp_match = 100 if job.experience_min <= user_exp else max(0, 100 - (job.experience_min - user_exp) * 20)
        
        # Combined score
        total_score = int(match_score * 0.7 + exp_match * 0.3)
        
        if total_score > 20:  # Only recommend if decent match
            skills = json.loads(job.skills_required) if job.skills_required else []
            matched_skills = [s for s in skills if s.lower() in user_skills]
            
            scored_jobs.append({
                'id': job.id,
                'title': job.title,
                'company': job.company,
                'location': job.location,
                'match_score': total_score,
                'matched_skills': matched_skills,
                'total_skills': len(skills),
                'salary_min': job.salary_min,
                'salary_max': job.salary_max
            })
    
    # Sort by score and return top 10
    scored_jobs.sort(key=lambda x: x['match_score'], reverse=True)
    
    return jsonify({
        'success': True,
        'recommendations': scored_jobs[:10],
        'user_skills': user_skills
    })

@jobs_bp.route('/<int:job_id>')
def job_detail(job_id):
    job = Job.query.get_or_404(job_id)
    
    # Check if user has already applied
    has_applied = False
    application = None
    match_info = None
    
    if current_user.is_authenticated:
        application = Application.query.filter_by(job_id=job_id, user_id=current_user.id).first()
        has_applied = application is not None
        
        # Calculate match for logged-in seekers
        if current_user.role == 'seeker':
            user_skills = get_user_skills(current_user)
            job_skills = []
            if job.skills_required:
                try:
                    job_skills = json.loads(job.skills_required)
                except:
                    job_skills = [s.strip() for s in job.skills_required.split(',')]
            
            job_skills_lower = set([s.lower() for s in job_skills])
            matched = [s for s in job_skills if s.lower() in user_skills]
            missing = [s for s in job_skills if s.lower() not in user_skills]
            
            match_info = {
                'percentage': int((len(matched) / len(job_skills_lower)) * 100) if job_skills_lower else 50,
                'matched': matched,
                'missing': missing
            }
    
    # Parse skills if stored as JSON
    skills = []
    if job.skills_required:
        try:
            skills = json.loads(job.skills_required)
        except:
            skills = [s.strip() for s in job.skills_required.split(',')]
    
    # Get similar jobs (same location or similar skills)
    similar_jobs = Job.query.filter(
        Job.id != job_id,
        Job.is_active == True
    ).limit(4).all()
    
    return render_template('jobs/detail.html', 
                         job=job, 
                         skills=skills, 
                         has_applied=has_applied,
                         application=application,
                         similar_jobs=similar_jobs,
                         match_info=match_info)

@jobs_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_job():
    if current_user.role != 'employer':
        return redirect(url_for('jobs_bp.jobs_list'))
    
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        skills_list = data.get('skills', '').split(',') if isinstance(data.get('skills'), str) else data.get('skills', [])
        
        job = Job(
            employer_id=current_user.id,
            title=data.get('title'),
            company=data.get('company') or current_user.company_name or 'Company',
            description=data.get('description'),
            requirements=data.get('requirements'),
            skills_required=json.dumps([s.strip() for s in skills_list if s.strip()]),
            experience_min=int(data.get('experience_min', 0)) if data.get('experience_min') else 0,
            experience_max=int(data.get('experience_max', 0)) if data.get('experience_max') else None,
            salary_min=int(data.get('salary_min', 0)) if data.get('salary_min') else None,
            salary_max=int(data.get('salary_max', 0)) if data.get('salary_max') else None,
            location=data.get('location'),
            job_type=data.get('job_type', 'full-time')
        )
        
        db.session.add(job)
        db.session.commit()
        
        if request.is_json:
            return jsonify({'success': True, 'job_id': job.id})
        return redirect(url_for('jobs_bp.job_detail', job_id=job.id))
    
    return render_template('jobs/create.html')

@jobs_bp.route('/<int:job_id>/apply', methods=['POST'])
@login_required
def apply_job(job_id):
    from modules.resume_ai import analyze_application
    from modules.letter_generator import generate_letter
    
    if current_user.role != 'seeker':
        return jsonify({'success': False, 'message': 'Only job seekers can apply'})
    
    job = Job.query.get_or_404(job_id)
    
    # Check if already applied
    existing = Application.query.filter_by(job_id=job_id, user_id=current_user.id).first()
    if existing:
        return jsonify({'success': False, 'message': 'You have already applied for this job'})
    
    # Run AI analysis
    analysis = analyze_application(current_user, job)
    
    # Create application
    application = Application(
        job_id=job_id,
        user_id=current_user.id,
        status=analysis['decision'],
        ai_score=analysis['overall_score'],
        match_percentage=analysis['match_percentage'],
        skills_match=json.dumps(analysis.get('matched_skills', [])),
        missing_skills=json.dumps(analysis.get('missing_skills', [])),
        feedback=json.dumps(analysis.get('feedback', {}))
    )
    
    # Generate letter if decision is made
    if analysis['decision'] in ['approved', 'rejected']:
        letter_path = generate_letter(current_user, job, analysis)
        application.letter_path = letter_path
        application.decided_at = datetime.utcnow()
    
    db.session.add(application)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'application_id': application.id,
        'status': application.status,
        'score': application.ai_score,
        'match_percentage': analysis['match_percentage'],
        'matched_skills': analysis.get('matched_skills', []),
        'missing_skills': analysis.get('missing_skills', []),
        'feedback': analysis.get('feedback', {}),
        'letter_path': application.letter_path
    })

@jobs_bp.route('/<int:job_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_job(job_id):
    job = Job.query.get_or_404(job_id)
    
    if job.employer_id != current_user.id:
        return redirect(url_for('jobs_bp.jobs_list'))
    
    if request.method == 'POST':
        data = request.form
        
        job.title = data.get('title', job.title)
        job.description = data.get('description', job.description)
        job.requirements = data.get('requirements', job.requirements)
        job.location = data.get('location', job.location)
        job.job_type = data.get('job_type', job.job_type)
        job.salary_min = int(data.get('salary_min')) if data.get('salary_min') else job.salary_min
        job.salary_max = int(data.get('salary_max')) if data.get('salary_max') else job.salary_max
        
        if data.get('skills'):
            skills = [s.strip() for s in data.get('skills').split(',')]
            job.skills_required = json.dumps(skills)
        
        db.session.commit()
        
        return redirect(url_for('jobs_bp.job_detail', job_id=job.id))
    
    return render_template('jobs/edit.html', job=job)

@jobs_bp.route('/<int:job_id>/toggle', methods=['POST'])
@login_required
def toggle_job(job_id):
    job = Job.query.get_or_404(job_id)
    
    if job.employer_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    job.is_active = not job.is_active
    db.session.commit()
    
    return jsonify({'success': True, 'is_active': job.is_active})

@jobs_bp.route('/<int:job_id>/applications')
@login_required
def job_applications(job_id):
    job = Job.query.get_or_404(job_id)
    
    if job.employer_id != current_user.id:
        return redirect(url_for('jobs_bp.jobs_list'))
    
    applications = Application.query.filter_by(job_id=job_id).order_by(Application.ai_score.desc()).all()
    
    return render_template('jobs/applications.html', job=job, applications=applications)
