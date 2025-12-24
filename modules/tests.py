from flask import Blueprint, render_template, request, jsonify, redirect, url_for, current_app, send_file
from flask_login import login_required, current_user
from datetime import datetime
import json
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch

from extensions import db
from models import User, PsychologicalTest, PsychologicalTestResult, SkillTest, SkillTestResult, Certificate

tests_bp = Blueprint('tests_bp', __name__, url_prefix='/tests')

@tests_bp.route('/')
@login_required
def index():
    psych_tests = PsychologicalTest.query.all()
    skill_tests = SkillTest.query.all()
    
    # Get user's completed tests
    completed_psych = {r.test_id: r for r in PsychologicalTestResult.query.filter_by(user_id=current_user.id).all()}
    completed_skill = {r.test_id: r for r in SkillTestResult.query.filter_by(user_id=current_user.id).all()}
    
    return render_template('tests/index.html', 
                           psych_tests=psych_tests, 
                           skill_tests=skill_tests,
                           completed_psych=completed_psych,
                           completed_skill=completed_skill)

@tests_bp.route('/psychological/<int:test_id>')
@login_required
def take_psych_test(test_id):
    test = PsychologicalTest.query.get_or_404(test_id)
    questions = json.loads(test.questions_json)
    return render_template('tests/take_psych.html', test=test, questions=questions)

@tests_bp.route('/psychological/<int:test_id>/submit', methods=['POST'])
@login_required
def submit_psych_test(test_id):
    test = PsychologicalTest.query.get_or_404(test_id)
    data = request.form
    
    # Simple scoring logic: sum of numerical values
    score = 0
    responses = {}
    for key, value in data.items():
        if key.startswith('q_'):
            score += int(value)
            responses[key] = value
            
    # Generate analysis based on score
    analysis = "Your psychological profile indicates a balanced professional approach."
    if score > 40:
        analysis = "You show high leadership potential and strong emotional intelligence."
    elif score < 20:
        analysis = "You are highly detail-oriented and prefer structured environments."
        
    result = PsychologicalTestResult(
        user_id=current_user.id,
        test_id=test_id,
        score=score,
        analysis=analysis
    )
    db.session.add(result)
    db.session.commit()
    
    # Generate certificate
    generate_test_certificate(result, 'psychology')
    
    return redirect(url_for('tests_bp.test_result', result_id=result.id, type='psychology'))

@tests_bp.route('/skill/<int:test_id>')
@login_required
def take_skill_test(test_id):
    test = SkillTest.query.get_or_404(test_id)
    questions = json.loads(test.questions_json)
    return render_template('tests/take_skill.html', test=test, questions=questions)

@tests_bp.route('/skill/<int:test_id>/submit', methods=['POST'])
@login_required
def submit_skill_test(test_id):
    test = SkillTest.query.get_or_404(test_id)
    questions = json.loads(test.questions_json)
    data = request.form
    
    correct_count = 0
    for i, q in enumerate(questions):
        answer = data.get(f'q_{i}')
        if answer == q.get('correct'):
            correct_count += 1
            
    score = int((correct_count / len(questions)) * 100)
    is_passed = score >= 70
    
    result = SkillTestResult(
        user_id=current_user.id,
        test_id=test_id,
        score=score,
        is_passed=is_passed
    )
    db.session.add(result)
    db.session.commit()
    
    if is_passed:
        generate_test_certificate(result, 'skill')
        
    return redirect(url_for('tests_bp.test_result', result_id=result.id, type='skill'))

@tests_bp.route('/result/<int:result_id>')
@login_required
def test_result(result_id):
    test_type = request.args.get('type')
    if test_type == 'psychology':
        result = PsychologicalTestResult.query.get_or_404(result_id)
        test = PsychologicalTest.query.get(result.test_id)
    else:
        result = SkillTestResult.query.get_or_404(result_id)
        test = SkillTest.query.get(result.test_id)
        
    certificate = Certificate.query.filter_by(
        user_id=current_user.id, 
        cert_type=test_type, 
        reference_id=result_id
    ).first()
    
    return render_template('tests/result.html', result=result, test=test, type=test_type, certificate=certificate)

def generate_test_certificate(result, cert_type):
    """Generate a PDF certificate for the test result"""
    cert_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'certificates')
    os.makedirs(cert_dir, exist_ok=True)
    
    filename = f"cert_{cert_type}_{result.id}.pdf"
    filepath = os.path.join(cert_dir, filename)
    
    # Get test info
    if cert_type == 'psychology':
        test = PsychologicalTest.query.get(result.test_id)
        title = f"Psychological Assessment: {test.title}"
    else:
        test = SkillTest.query.get(result.test_id)
        title = f"Skill Certification: {test.skill_name}"
        
    # PDF generation
    c = canvas.Canvas(filepath, pagesize=letter)
    width, height = letter
    
    # Border
    c.setStrokeColor(colors.gold)
    c.setLineWidth(5)
    c.rect(0.5*inch, 0.5*inch, width-1*inch, height-1*inch)
    
    # Content
    c.setFont("Helvetica-Bold", 30)
    c.drawCentredString(width/2, height - 2*inch, "CERTIFICATE OF COMPLETION")
    
    c.setFont("Helvetica", 18)
    c.drawCentredString(width/2, height - 3*inch, "This is to certify that")
    
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width/2, height - 4*inch, current_user.name.upper())
    
    c.setFont("Helvetica", 18)
    c.drawCentredString(width/2, height - 5*inch, "has successfully completed the")
    
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width/2, height - 6*inch, title)
    
    if cert_type == 'skill':
        c.setFont("Helvetica", 16)
        c.drawCentredString(width/2, height - 6.5*inch, f"with a score of {result.score}%")
    
    c.setFont("Helvetica", 14)
    c.drawCentredString(width/2, height - 8*inch, f"Date: {datetime.utcnow().strftime('%B %d, %Y')}")
    c.drawCentredString(width/2, height - 8.5*inch, f"Certificate ID: JOB-{cert_type[:3].upper()}-{result.id}")
    
    c.save()
    
    # Save search record in DB
    cert = Certificate(
        user_id=current_user.id,
        cert_type=cert_type,
        reference_id=result.id,
        title=title,
        file_path=f"/static/uploads/certificates/{filename}"
    )
    db.session.add(cert)
    db.session.commit()
    
    return cert.file_path
