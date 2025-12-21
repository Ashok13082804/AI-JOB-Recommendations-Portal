from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
import json
import re

from extensions import db
from models import Resume, Skill, Experience, Education
from config import Config

resume_bp = Blueprint('resume_bp', __name__, url_prefix='/resume')

# Common tech skills database
TECH_SKILLS = {
    'programming': ['python', 'javascript', 'java', 'c++', 'c#', 'go', 'rust', 'ruby', 'php', 'swift', 'kotlin', 'typescript', 'scala', 'r'],
    'frontend': ['html', 'css', 'react', 'vue', 'angular', 'svelte', 'jquery', 'bootstrap', 'tailwind', 'sass', 'less', 'webpack'],
    'backend': ['node.js', 'express', 'django', 'flask', 'fastapi', 'spring', 'laravel', 'rails', 'asp.net', 'graphql', 'rest api'],
    'database': ['mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'sqlite', 'oracle', 'sql server', 'cassandra', 'dynamodb'],
    'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'jenkins', 'ci/cd', 'devops', 'linux', 'nginx'],
    'data': ['machine learning', 'data science', 'pandas', 'numpy', 'tensorflow', 'pytorch', 'spark', 'hadoop', 'tableau', 'power bi'],
    'mobile': ['android', 'ios', 'react native', 'flutter', 'xamarin', 'swift', 'kotlin'],
    'tools': ['git', 'github', 'gitlab', 'jira', 'agile', 'scrum', 'figma', 'postman', 'vs code']
}

# Flatten skills list for matching
ALL_SKILLS = set()
for category in TECH_SKILLS.values():
    ALL_SKILLS.update([s.lower() for s in category])

def extract_text_from_pdf(file_path):
    """Extract text from PDF file"""
    try:
        import pdfplumber
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text.strip()
    except Exception as e:
        print(f"PDF extraction error: {e}")
        return ""

def extract_skills(text):
    """Extract skills from resume text"""
    text_lower = text.lower()
    found_skills = []
    
    for skill in ALL_SKILLS:
        # Check for skill with word boundaries
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found_skills.append(skill)
    
    return list(set(found_skills))

def extract_experience(text):
    """Extract years of experience from resume"""
    experience_patterns = [
        r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*experience',
        r'experience\s*(?:of)?\s*(\d+)\+?\s*(?:years?|yrs?)',
        r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:in|working)',
    ]
    
    max_years = 0
    for pattern in experience_patterns:
        matches = re.findall(pattern, text.lower())
        for match in matches:
            years = int(match)
            if years > max_years and years < 50:  # Sanity check
                max_years = years
    
    return max_years

def extract_education(text):
    """Extract education keywords"""
    education_keywords = ['bachelor', 'master', 'phd', 'b.tech', 'm.tech', 'bsc', 'msc', 'mba', 
                         'b.e', 'm.e', 'diploma', 'degree', 'university', 'college']
    
    text_lower = text.lower()
    found = []
    
    for keyword in education_keywords:
        if keyword in text_lower:
            found.append(keyword)
    
    return found

def extract_contact_info(text):
    """Extract contact information"""
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    phone_pattern = r'[\+]?[(]?[0-9]{1,3}[)]?[-\s\.]?[0-9]{3,4}[-\s\.]?[0-9]{4,6}'
    
    emails = re.findall(email_pattern, text)
    phones = re.findall(phone_pattern, text)
    
    return {
        'email': emails[0] if emails else None,
        'phone': phones[0] if phones else None
    }

def calculate_ats_score(resume_data):
    """Calculate ATS score based on resume structure and content"""
    score = 0
    max_score = 100
    feedback = []
    
    # Skills (35 points)
    skills_count = len(resume_data.get('skills', []))
    if skills_count >= 10:
        score += 35
    elif skills_count >= 5:
        score += 25
        feedback.append("Add more relevant skills to improve your score")
    elif skills_count >= 3:
        score += 15
        feedback.append("Your resume needs more technical skills")
    else:
        score += 5
        feedback.append("Missing technical skills section")
    
    # Experience (25 points)
    experience = resume_data.get('experience_years', 0)
    if experience >= 5:
        score += 25
    elif experience >= 3:
        score += 20
    elif experience >= 1:
        score += 15
    else:
        score += 5
        feedback.append("Add your work experience with dates")
    
    # Education (15 points)
    education = resume_data.get('education', [])
    if len(education) >= 2:
        score += 15
    elif len(education) >= 1:
        score += 10
    else:
        feedback.append("Include your educational qualifications")
    
    # Contact info (10 points)
    contact = resume_data.get('contact', {})
    if contact.get('email') and contact.get('phone'):
        score += 10
    elif contact.get('email') or contact.get('phone'):
        score += 5
        feedback.append("Include both email and phone number")
    else:
        feedback.append("Missing contact information")
    
    # Content length (15 points)
    text_length = len(resume_data.get('raw_text', ''))
    if text_length >= 2000:
        score += 15
    elif text_length >= 1000:
        score += 10
    elif text_length >= 500:
        score += 5
        feedback.append("Resume content is too brief - add more details")
    else:
        feedback.append("Resume is too short - elaborate on your experience")
    
    return {
        'score': min(score, max_score),
        'feedback': feedback
    }

def parse_resume(file_path):
    """Parse resume and extract all relevant information"""
    text = extract_text_from_pdf(file_path)
    
    if not text:
        return {
            'success': False,
            'message': 'Could not extract text from PDF'
        }
    
    resume_data = {
        'raw_text': text,
        'skills': extract_skills(text),
        'experience_years': extract_experience(text),
        'education': extract_education(text),
        'contact': extract_contact_info(text)
    }
    
    ats_result = calculate_ats_score(resume_data)
    resume_data['ats_score'] = ats_result['score']
    resume_data['ats_feedback'] = ats_result['feedback']
    
    return {
        'success': True,
        'data': resume_data
    }

def match_job_requirements(resume_data, job_data):
    """Match resume skills with job requirements"""
    resume_skills = set([s.lower() for s in resume_data.get('skills', [])])
    
    # Parse job skills
    job_skills = []
    if job_data.get('skills_required'):
        try:
            job_skills = json.loads(job_data['skills_required'])
        except:
            job_skills = [s.strip() for s in job_data.get('skills_required', '').split(',')]
    
    job_skills_set = set([s.lower().strip() for s in job_skills])
    
    # Calculate matches
    matched = resume_skills.intersection(job_skills_set)
    missing = job_skills_set - resume_skills
    
    if len(job_skills_set) > 0:
        match_percentage = int((len(matched) / len(job_skills_set)) * 100)
    else:
        match_percentage = 50  # Default if no skills specified
    
    return {
        'matched_skills': list(matched),
        'missing_skills': list(missing),
        'match_percentage': match_percentage
    }

def analyze_application(user, job):
    """Analyze a job application and make AI decision"""
    # Get user's resume data
    resume = Resume.query.filter_by(user_id=user.id).first()
    
    # Build resume data from profile if no parsed resume
    if resume and resume.parsed_data:
        try:
            resume_data = json.loads(resume.parsed_data)
        except:
            resume_data = {}
    else:
        # Use profile data
        user_skills = [skill.name.lower() for skill in Skill.query.filter_by(user_id=user.id).all()]
        user_experiences = Experience.query.filter_by(user_id=user.id).all()
        user_educations = Education.query.filter_by(user_id=user.id).all()
        
        # Calculate experience years
        from datetime import date
        total_months = 0
        for exp in user_experiences:
            if exp.start_date:
                end = exp.end_date if exp.end_date else date.today()
                months = (end.year - exp.start_date.year) * 12 + (end.month - exp.start_date.month)
                total_months += max(0, months)
        
        resume_data = {
            'skills': user_skills,
            'experience_years': total_months // 12,
            'education': [edu.degree for edu in user_educations],
            'ats_score': resume.ats_score if resume else 50
        }
    
    # Get job data
    job_data = {
        'title': job.title,
        'skills_required': job.skills_required,
        'experience_min': job.experience_min or 0,
        'experience_max': job.experience_max
    }
    
    # Match skills
    match_result = match_job_requirements(resume_data, job_data)
    
    # Calculate overall score
    ats_score = resume_data.get('ats_score', 50)
    skill_score = match_result['match_percentage']
    
    # Experience score
    user_exp = resume_data.get('experience_years', 0)
    exp_required = job.experience_min or 0
    
    if user_exp >= exp_required:
        exp_score = 100
    elif user_exp >= exp_required - 1:
        exp_score = 75
    else:
        exp_score = max(0, 50 - (exp_required - user_exp) * 10)
    
    # Profile completeness
    profile_score = 70  # Default
    if user.headline and user.bio:
        profile_score = 100
    elif user.headline or user.bio:
        profile_score = 85
    
    # Calculate weighted overall score
    weights = Config.RESUME_WEIGHTS
    overall_score = int(
        skill_score * weights['skills_match'] +
        exp_score * weights['experience_match'] +
        (profile_score * 0.5 + ats_score * 0.5) * weights['education_match'] +
        ats_score * weights['format_score'] +
        skill_score * weights['keywords_match']
    )
    
    # Make decision
    if overall_score >= Config.AUTO_APPROVE_THRESHOLD:
        decision = 'approved'
    elif overall_score <= Config.AUTO_REJECT_THRESHOLD:
        decision = 'rejected'
    else:
        decision = 'under_review'
    
    # Generate feedback
    feedback = generate_feedback(resume_data, job_data, match_result, decision)
    
    return {
        'overall_score': overall_score,
        'match_percentage': match_result['match_percentage'],
        'matched_skills': match_result['matched_skills'],
        'missing_skills': match_result['missing_skills'],
        'experience_score': exp_score,
        'ats_score': ats_score,
        'decision': decision,
        'feedback': feedback
    }

def generate_feedback(resume_data, job_data, match_result, decision):
    """Generate detailed feedback for the applicant"""
    feedback = {
        'strengths': [],
        'improvements': [],
        'recommendations': []
    }
    
    # Strengths
    if len(match_result['matched_skills']) > 3:
        feedback['strengths'].append(f"Strong skill match with {len(match_result['matched_skills'])} relevant skills")
    
    if resume_data.get('experience_years', 0) >= (job_data.get('experience_min', 0)):
        feedback['strengths'].append("Experience level meets job requirements")
    
    if resume_data.get('ats_score', 0) >= 70:
        feedback['strengths'].append("Well-formatted, ATS-friendly resume")
    
    # Improvements needed
    if match_result['missing_skills']:
        missing = match_result['missing_skills'][:5]
        feedback['improvements'].append(f"Missing key skills: {', '.join(missing)}")
    
    if resume_data.get('ats_score', 0) < 70:
        feedback['improvements'].append("Resume formatting needs improvement for better ATS compatibility")
    
    exp_gap = (job_data.get('experience_min', 0) - resume_data.get('experience_years', 0))
    if exp_gap > 0:
        feedback['improvements'].append(f"Experience gap: {exp_gap} more year(s) needed")
    
    # Recommendations
    if match_result['missing_skills']:
        skill_courses = {
            'react': 'React - The Complete Guide on Udemy',
            'python': 'Python for Everybody by University of Michigan',
            'aws': 'AWS Certified Solutions Architect on A Cloud Guru',
            'docker': 'Docker Mastery on Udemy',
            'machine learning': 'Machine Learning by Andrew Ng on Coursera'
        }
        
        for skill in match_result['missing_skills'][:3]:
            if skill.lower() in skill_courses:
                feedback['recommendations'].append(f"Learn {skill}: {skill_courses[skill.lower()]}")
            else:
                feedback['recommendations'].append(f"Consider learning {skill} to improve your profile")
    
    if decision == 'rejected':
        feedback['recommendations'].append("Update your resume with more relevant keywords")
        feedback['recommendations'].append("Add more project descriptions highlighting your skills")
    
    return feedback

@resume_bp.route('/upload', methods=['POST'])
@login_required
def upload_resume():
    """Upload and parse a resume"""
    if 'resume' not in request.files:
        return jsonify({'success': False, 'message': 'No file uploaded'})
    
    file = request.files['resume']
    
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'})
    
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'success': False, 'message': 'Only PDF files are allowed'})
    
    # Save file
    filename = secure_filename(f"{current_user.id}_{file.filename}")
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'resumes', filename)
    file.save(file_path)
    
    # Parse resume
    result = parse_resume(file_path)
    
    if not result['success']:
        return jsonify(result)
    
    resume_data = result['data']
    
    # Save to database
    resume = Resume.query.filter_by(user_id=current_user.id).first()
    if not resume:
        resume = Resume(user_id=current_user.id)
    
    resume.file_path = f"/static/uploads/resumes/{filename}"
    resume.ats_score = resume_data['ats_score']
    resume.skills_extracted = json.dumps(resume_data['skills'])
    resume.keywords = json.dumps(resume_data.get('keywords', []))
    resume.parsed_data = json.dumps(resume_data)
    
    db.session.add(resume)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'ats_score': resume_data['ats_score'],
        'skills': resume_data['skills'],
        'feedback': resume_data['ats_feedback'],
        'file_path': resume.file_path
    })

@resume_bp.route('/analyze')
@login_required
def analyze_resume():
    """Get resume analysis for current user"""
    resume = Resume.query.filter_by(user_id=current_user.id).first()
    
    if not resume:
        return jsonify({'success': False, 'message': 'No resume uploaded'})
    
    try:
        parsed_data = json.loads(resume.parsed_data) if resume.parsed_data else {}
    except:
        parsed_data = {}
    
    return jsonify({
        'success': True,
        'ats_score': resume.ats_score,
        'skills': json.loads(resume.skills_extracted) if resume.skills_extracted else [],
        'parsed_data': parsed_data
    })
