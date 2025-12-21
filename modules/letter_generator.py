"""
Letter Generator Module
Generates PDF offer letters and rejection letters with detailed feedback
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime
import os

def generate_letter(user, job, analysis):
    """Generate appropriate letter based on application decision"""
    if analysis['decision'] == 'approved':
        return generate_offer_letter(user, job, analysis)
    elif analysis['decision'] == 'rejected':
        return generate_rejection_letter(user, job, analysis)
    return None

def get_styles():
    """Get custom paragraph styles"""
    styles = getSampleStyleSheet()
    
    # Only add styles if they don't already exist
    if 'CustomTitle' not in styles.byName:
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#0a66c2')
        ))
    
    if 'CompanyName' not in styles.byName:
        styles.add(ParagraphStyle(
            name='CompanyName',
            parent=styles['Normal'],
            fontSize=18,
            spaceAfter=5,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1a1a1a'),
            fontName='Helvetica-Bold'
        ))
    
    if 'SubTitle' not in styles.byName:
        styles.add(ParagraphStyle(
            name='SubTitle',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.grey
        ))
    
    if 'CustomBody' not in styles.byName:
        styles.add(ParagraphStyle(
            name='CustomBody',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            alignment=TA_JUSTIFY,
            leading=16
        ))
    
    if 'SectionHeader' not in styles.byName:
        styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=styles['Heading2'],
            fontSize=14,
            spaceBefore=20,
            spaceAfter=10,
            textColor=colors.HexColor('#0a66c2')
        ))
    
    if 'ListItem' not in styles.byName:
        styles.add(ParagraphStyle(
            name='ListItem',
            parent=styles['Normal'],
            fontSize=11,
            leftIndent=20,
            spaceAfter=8,
            bulletIndent=10
        ))
    
    if 'Footer' not in styles.byName:
        styles.add(ParagraphStyle(
            name='Footer',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.grey,
            alignment=TA_CENTER
        ))
    
    return styles

def generate_offer_letter(user, job, analysis):
    """Generate a professional offer letter PDF"""
    # Create filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"offer_letter_{user.id}_{job.id}_{timestamp}.pdf"
    file_path = os.path.join('static', 'uploads', 'letters', filename)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Create PDF
    doc = SimpleDocTemplate(file_path, pagesize=letter, 
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=72)
    
    styles = get_styles()
    story = []
    
    # Header
    story.append(Paragraph(job.company or "Company", styles['CompanyName']))
    story.append(Paragraph("OFFER LETTER", styles['CustomTitle']))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#0a66c2')))
    story.append(Spacer(1, 20))
    
    # Date
    story.append(Paragraph(f"Date: {datetime.now().strftime('%B %d, %Y')}", styles['CustomBody']))
    story.append(Spacer(1, 10))
    
    # Recipient
    story.append(Paragraph(f"Dear <b>{user.name}</b>,", styles['CustomBody']))
    story.append(Spacer(1, 10))
    
    # Main content
    story.append(Paragraph(
        f"""We are delighted to inform you that based on our comprehensive AI-powered evaluation 
        of your profile, you have been selected for the position of <b>{job.title}</b> at 
        <b>{job.company}</b>. Congratulations!""",
        styles['CustomBody']
    ))
    
    story.append(Paragraph(
        f"""Your application received an impressive match score of <b>{analysis['overall_score']}%</b>, 
        demonstrating excellent alignment with our requirements. Your skills and experience stood out 
        among all applicants.""",
        styles['CustomBody']
    ))
    
    # Position Details
    story.append(Paragraph("Position Details", styles['SectionHeader']))
    
    position_data = [
        ['Position:', job.title],
        ['Company:', job.company or 'Company'],
        ['Location:', job.location or 'To be discussed'],
        ['Job Type:', job.job_type or 'Full-time'],
    ]
    
    if job.salary_min:
        salary = f"₹{job.salary_min:,}"
        if job.salary_max:
            salary += f" - ₹{job.salary_max:,}"
        salary += " per annum"
        position_data.append(['Salary:', salary])
    
    position_table = Table(position_data, colWidths=[120, 350])
    position_table.setStyle(TableStyle([
        ('FONT', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONT', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#0a66c2')),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
    ]))
    story.append(position_table)
    story.append(Spacer(1, 15))
    
    # Matched Skills
    if analysis.get('matched_skills'):
        story.append(Paragraph("Your Matching Skills", styles['SectionHeader']))
        skills_text = ", ".join(analysis['matched_skills'][:10])
        story.append(Paragraph(f"<b>{skills_text}</b>", styles['CustomBody']))
        story.append(Spacer(1, 10))
    
    # Next Steps
    story.append(Paragraph("Next Steps", styles['SectionHeader']))
    story.append(Paragraph("• Our HR team will contact you within 3-5 business days", styles['ListItem']))
    story.append(Paragraph("• You will receive further documentation for onboarding", styles['ListItem']))
    story.append(Paragraph("• Please respond to confirm your acceptance", styles['ListItem']))
    
    story.append(Spacer(1, 20))
    
    # Closing
    story.append(Paragraph(
        "We are excited about the prospect of you joining our team and look forward to your positive response.",
        styles['CustomBody']
    ))
    
    story.append(Spacer(1, 30))
    story.append(Paragraph("Best Regards,", styles['CustomBody']))
    story.append(Paragraph(f"<b>HR Team</b><br/>{job.company}", styles['CustomBody']))
    
    # Footer
    story.append(Spacer(1, 40))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "This offer letter was automatically generated by SkillMatch AI Job Portal. "
        f"Reference: APP-{user.id}-{job.id}-{timestamp}",
        styles['Footer']
    ))
    
    doc.build(story)
    
    return f"/static/uploads/letters/{filename}"

def generate_rejection_letter(user, job, analysis):
    """Generate a rejection letter with detailed feedback"""
    # Create filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"feedback_letter_{user.id}_{job.id}_{timestamp}.pdf"
    file_path = os.path.join('static', 'uploads', 'letters', filename)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Create PDF
    doc = SimpleDocTemplate(file_path, pagesize=letter,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=72)
    
    styles = get_styles()
    story = []
    
    # Header
    story.append(Paragraph(job.company or "Company", styles['CompanyName']))
    story.append(Paragraph("APPLICATION FEEDBACK", styles['CustomTitle']))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#666666')))
    story.append(Spacer(1, 20))
    
    # Date
    story.append(Paragraph(f"Date: {datetime.now().strftime('%B %d, %Y')}", styles['CustomBody']))
    story.append(Spacer(1, 10))
    
    # Recipient
    story.append(Paragraph(f"Dear <b>{user.name}</b>,", styles['CustomBody']))
    story.append(Spacer(1, 10))
    
    # Main content
    story.append(Paragraph(
        f"""Thank you for your interest in the <b>{job.title}</b> position at <b>{job.company}</b> 
        and for taking the time to apply. We appreciate your effort and the opportunity to learn 
        about your background and skills.""",
        styles['CustomBody']
    ))
    
    story.append(Paragraph(
        f"""After careful evaluation of your application using our AI-powered assessment system, 
        we regret to inform you that we are unable to proceed with your candidacy at this time. 
        Your profile scored <b>{analysis['overall_score']}%</b>, which falls below our threshold 
        for this particular role.""",
        styles['CustomBody']
    ))
    
    story.append(Paragraph(
        "Please note that this decision does not reflect on your overall abilities or potential. "
        "Below, we provide detailed feedback to help you improve your chances in future applications.",
        styles['CustomBody']
    ))
    
    # Analysis Summary
    story.append(Paragraph("Your Application Analysis", styles['SectionHeader']))
    
    analysis_data = [
        ['Overall Match Score:', f"{analysis['overall_score']}%"],
        ['Skills Match:', f"{analysis['match_percentage']}%"],
        ['ATS Score:', f"{analysis.get('ats_score', 50)}%"],
    ]
    
    analysis_table = Table(analysis_data, colWidths=[150, 100])
    analysis_table.setStyle(TableStyle([
        ('FONT', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fff3f3')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#ffcccc')),
    ]))
    story.append(analysis_table)
    story.append(Spacer(1, 15))
    
    # Skills Gap
    if analysis.get('missing_skills'):
        story.append(Paragraph("Missing Skills for This Role", styles['SectionHeader']))
        for skill in analysis['missing_skills'][:8]:
            story.append(Paragraph(f"• {skill}", styles['ListItem']))
        story.append(Spacer(1, 10))
    
    # Feedback
    feedback = analysis.get('feedback', {})
    
    if feedback.get('strengths'):
        story.append(Paragraph("Your Strengths", styles['SectionHeader']))
        for strength in feedback['strengths'][:5]:
            story.append(Paragraph(f"✓ {strength}", styles['ListItem']))
        story.append(Spacer(1, 10))
    
    if feedback.get('improvements'):
        story.append(Paragraph("Areas for Improvement", styles['SectionHeader']))
        for improvement in feedback['improvements'][:5]:
            story.append(Paragraph(f"• {improvement}", styles['ListItem']))
        story.append(Spacer(1, 10))
    
    if feedback.get('recommendations'):
        story.append(Paragraph("Recommendations", styles['SectionHeader']))
        for rec in feedback['recommendations'][:5]:
            story.append(Paragraph(f"→ {rec}", styles['ListItem']))
        story.append(Spacer(1, 10))
    
    # Encouragement
    story.append(Paragraph("Moving Forward", styles['SectionHeader']))
    story.append(Paragraph(
        "We encourage you to continue developing your skills and to reapply for future openings "
        "that match your profile. Our job portal is continuously updated with new opportunities.",
        styles['CustomBody']
    ))
    
    story.append(Paragraph(
        "Tips to improve your candidacy:",
        styles['CustomBody']
    ))
    story.append(Paragraph("• Update your resume with relevant keywords and quantified achievements", styles['ListItem']))
    story.append(Paragraph("• Complete online courses for skills you're missing", styles['ListItem']))
    story.append(Paragraph("• Ensure your resume is ATS-friendly with clear formatting", styles['ListItem']))
    story.append(Paragraph("• Build projects that showcase your technical abilities", styles['ListItem']))
    
    story.append(Spacer(1, 20))
    
    # Closing
    story.append(Paragraph(
        "We wish you all the best in your job search and future career endeavors.",
        styles['CustomBody']
    ))
    
    story.append(Spacer(1, 30))
    story.append(Paragraph("Best Regards,", styles['CustomBody']))
    story.append(Paragraph(f"<b>HR Team</b><br/>{job.company}", styles['CustomBody']))
    
    # Footer
    story.append(Spacer(1, 40))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "This feedback letter was automatically generated by SkillMatch AI Job Portal. "
        f"Reference: FEEDBACK-{user.id}-{job.id}-{timestamp}",
        styles['Footer']
    ))
    
    doc.build(story)
    
    return f"/static/uploads/letters/{filename}"
