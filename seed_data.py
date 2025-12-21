"""
Seed data script to populate the database with sample jobs and users
Run this after starting the app to have demo data
"""
from app import app, db
from models import User, Job, Skill, Experience, Education
from werkzeug.security import generate_password_hash
from datetime import datetime, date
import json

def seed_database():
    with app.app_context():
        # Check if data already exists
        if Job.query.count() > 0:
            print("Database already has data, skipping seed.")
            return
        
        print("Seeding database with sample data...")
        
        # Create sample employer
        employer = User(
            email="employer@techcorp.com",
            password_hash=generate_password_hash("password123"),
            name="TechCorp HR",
            role="employer",
            company_name="TechCorp Solutions",
            headline="Hiring Manager at TechCorp",
            bio="We are a leading technology company looking for talented individuals."
        )
        db.session.add(employer)
        db.session.commit()
        
        # Create sample jobs
        jobs_data = [
            {
                "title": "Senior Frontend Developer",
                "company": "TechCorp Solutions",
                "description": """We are looking for an experienced Frontend Developer to join our team.

Responsibilities:
- Develop and maintain web applications using React
- Collaborate with UX designers to implement responsive designs
- Write clean, maintainable code with proper documentation
- Participate in code reviews and mentor junior developers
- Optimize applications for maximum speed and scalability""",
                "requirements": """- 5+ years of frontend development experience
- Strong proficiency in React, JavaScript, TypeScript
- Experience with state management (Redux, MobX)
- Knowledge of CSS frameworks and responsive design
- Familiarity with Git and CI/CD pipelines""",
                "skills_required": json.dumps(["React", "JavaScript", "TypeScript", "CSS", "Redux", "Git", "HTML", "Node.js"]),
                "experience_min": 5,
                "experience_max": 8,
                "salary_min": 1500000,
                "salary_max": 2500000,
                "location": "Bangalore",
                "job_type": "full-time"
            },
            {
                "title": "Python Backend Developer",
                "company": "DataTech Inc",
                "description": """Join our backend team to build scalable APIs and services.

What you'll do:
- Design and implement RESTful APIs using Python/Flask
- Work with databases (PostgreSQL, MongoDB, Redis)
- Implement microservices architecture
- Write unit tests and integration tests
- Deploy and maintain applications on AWS""",
                "requirements": """- 3+ years of Python development
- Experience with Flask or Django
- Strong SQL and NoSQL database skills
- Knowledge of Docker and Kubernetes
- Understanding of cloud services (AWS/GCP)""",
                "skills_required": json.dumps(["Python", "Flask", "Django", "PostgreSQL", "MongoDB", "Docker", "AWS", "REST API"]),
                "experience_min": 3,
                "experience_max": 6,
                "salary_min": 1200000,
                "salary_max": 2000000,
                "location": "Remote",
                "job_type": "remote"
            },
            {
                "title": "Full Stack Developer",
                "company": "StartupXYZ",
                "description": """Looking for a versatile developer who can handle both frontend and backend.

You will:
- Build features end-to-end from design to deployment
- Work with React on frontend and Node.js on backend
- Manage database schemas and optimization
- Integrate third-party APIs and services
- Contribute to architectural decisions""",
                "requirements": """- 2+ years of full-stack development
- Proficiency in JavaScript/TypeScript
- Experience with React and Node.js
- Database experience (SQL and NoSQL)
- Good understanding of web security""",
                "skills_required": json.dumps(["JavaScript", "React", "Node.js", "MongoDB", "Express", "TypeScript", "Git", "REST API"]),
                "experience_min": 2,
                "experience_max": 5,
                "salary_min": 800000,
                "salary_max": 1500000,
                "location": "Mumbai",
                "job_type": "full-time"
            },
            {
                "title": "Machine Learning Engineer",
                "company": "AI Labs",
                "description": """Join our AI team to build cutting-edge ML solutions.

Responsibilities:
- Develop and deploy machine learning models
- Work with large datasets for training and validation
- Implement NLP and computer vision solutions
- Optimize model performance and accuracy
- Collaborate with data scientists and engineers""",
                "requirements": """- 3+ years of ML/AI experience
- Strong Python and data science skills
- Experience with TensorFlow or PyTorch
- Knowledge of NLP and computer vision
- PhD or Masters in CS/ML preferred""",
                "skills_required": json.dumps(["Python", "Machine Learning", "TensorFlow", "PyTorch", "NLP", "Data Science", "Deep Learning", "Pandas"]),
                "experience_min": 3,
                "experience_max": 7,
                "salary_min": 2000000,
                "salary_max": 3500000,
                "location": "Hyderabad",
                "job_type": "full-time"
            },
            {
                "title": "DevOps Engineer",
                "company": "CloudFirst",
                "description": """We need a DevOps engineer to manage our cloud infrastructure.

You'll be responsible for:
- Managing AWS/GCP infrastructure
- Implementing CI/CD pipelines using Jenkins/GitLab
- Container orchestration with Kubernetes
- Infrastructure as Code using Terraform
- Monitoring and alerting systems""",
                "requirements": """- 4+ years of DevOps experience
- Expert knowledge of AWS or GCP
- Strong Kubernetes and Docker skills
- Experience with Terraform/Ansible
- Scripting in Python/Bash""",
                "skills_required": json.dumps(["AWS", "Docker", "Kubernetes", "Terraform", "Jenkins", "Linux", "Python", "CI/CD"]),
                "experience_min": 4,
                "experience_max": 8,
                "salary_min": 1800000,
                "salary_max": 3000000,
                "location": "Pune",
                "job_type": "full-time"
            },
            {
                "title": "React Native Developer",
                "company": "MobileApps Co",
                "description": """Build amazing mobile experiences with React Native.

What you'll do:
- Develop cross-platform mobile applications
- Implement UI/UX designs with pixel perfection
- Integrate with backend APIs
- Optimize app performance and battery usage
- Publish apps to App Store and Play Store""",
                "requirements": """- 2+ years of React Native experience
- Strong JavaScript/TypeScript skills
- Experience with native modules
- Knowledge of mobile app lifecycle
- Published apps on stores is a plus""",
                "skills_required": json.dumps(["React Native", "JavaScript", "TypeScript", "iOS", "Android", "Redux", "REST API"]),
                "experience_min": 2,
                "experience_max": 5,
                "salary_min": 1000000,
                "salary_max": 1800000,
                "location": "Chennai",
                "job_type": "full-time"
            },
            {
                "title": "Data Analyst",
                "company": "Analytics Pro",
                "description": """Turn data into actionable insights for our clients.

Responsibilities:
- Analyze large datasets to identify trends
- Create dashboards and visualizations
- Write SQL queries for data extraction
- Present findings to stakeholders
- Work with BI tools like Tableau/Power BI""",
                "requirements": """- 1+ years of data analysis experience
- Strong SQL skills
- Proficiency in Excel and visualization tools
- Knowledge of Python/R for analysis
- Good communication skills""",
                "skills_required": json.dumps(["SQL", "Python", "Tableau", "Excel", "Power BI", "Data Analysis", "Statistics"]),
                "experience_min": 1,
                "experience_max": 3,
                "salary_min": 600000,
                "salary_max": 1000000,
                "location": "Delhi",
                "job_type": "full-time"
            },
            {
                "title": "Java Developer",
                "company": "Enterprise Solutions",
                "description": """Join our team building enterprise Java applications.

You will:
- Develop microservices using Spring Boot
- Work with Oracle/PostgreSQL databases
- Implement REST and SOAP APIs
- Write unit and integration tests
- Follow Agile development practices""",
                "requirements": """- 3+ years of Java development
- Strong Spring/Spring Boot knowledge
- Experience with microservices architecture
- JUnit testing experience
- Knowledge of messaging systems (Kafka)""",
                "skills_required": json.dumps(["Java", "Spring Boot", "Microservices", "Oracle", "REST API", "Kafka", "JUnit"]),
                "experience_min": 3,
                "experience_max": 6,
                "salary_min": 1200000,
                "salary_max": 2200000,
                "location": "Noida",
                "job_type": "full-time"
            },
            {
                "title": "UI/UX Designer",
                "company": "Design Studio",
                "description": """Create beautiful and intuitive user experiences.

What you'll do:
- Design user interfaces for web and mobile apps
- Create wireframes, prototypes, and mockups
- Conduct user research and usability testing
- Collaborate with developers for implementation
- Define and maintain design systems""",
                "requirements": """- 2+ years of UI/UX design experience
- Proficiency in Figma/Sketch
- Understanding of user-centered design
- Basic knowledge of HTML/CSS
- Strong portfolio required""",
                "skills_required": json.dumps(["Figma", "UI Design", "UX Design", "Sketch", "Adobe XD", "Prototyping", "User Research"]),
                "experience_min": 2,
                "experience_max": 5,
                "salary_min": 800000,
                "salary_max": 1500000,
                "location": "Bangalore",
                "job_type": "full-time"
            },
            {
                "title": "Fresher Software Developer",
                "company": "TechStart",
                "description": """Great opportunity for freshers to start their career!

We're looking for enthusiastic freshers who:
- Have a passion for coding
- Are willing to learn new technologies
- Can work in a team environment
- Have basic programming knowledge

Training will be provided!""",
                "requirements": """- B.Tech/BE in Computer Science or related field
- Basic knowledge of any programming language
- Understanding of data structures and algorithms
- Good problem-solving skills
- Excellent communication skills""",
                "skills_required": json.dumps(["Java", "Python", "Data Structures", "Algorithms", "SQL", "Git"]),
                "experience_min": 0,
                "experience_max": 1,
                "salary_min": 400000,
                "salary_max": 600000,
                "location": "Bangalore",
                "job_type": "full-time"
            }
        ]
        
        for job_data in jobs_data:
            job = Job(
                employer_id=employer.id,
                **job_data
            )
            db.session.add(job)
        
        db.session.commit()
        print(f"Added {len(jobs_data)} sample jobs!")
        
        # Create sample job seeker
        seeker = User(
            email="john@example.com",
            password_hash=generate_password_hash("password123"),
            name="John Developer",
            role="seeker",
            headline="Full Stack Developer | React | Node.js | Python",
            bio="Passionate software developer with 3 years of experience building web applications."
        )
        db.session.add(seeker)
        db.session.commit()
        
        # Add skills for seeker
        seeker_skills = ["Python", "JavaScript", "React", "Node.js", "MongoDB", "Git", "Docker", "AWS", "HTML", "CSS"]
        for skill_name in seeker_skills:
            skill = Skill(user_id=seeker.id, name=skill_name, category="technical")
            db.session.add(skill)
        
        # Add experience
        exp = Experience(
            user_id=seeker.id,
            title="Software Developer",
            company="WebTech Solutions",
            location="Bangalore",
            start_date=date(2021, 6, 1),
            is_current=True,
            description="Developing web applications using React and Node.js"
        )
        db.session.add(exp)
        
        # Add education
        edu = Education(
            user_id=seeker.id,
            degree="B.Tech",
            institution="IIT Delhi",
            field="Computer Science",
            year=2021,
            grade="8.5 CGPA"
        )
        db.session.add(edu)
        
        db.session.commit()
        print("Added sample job seeker with skills, experience, and education!")
        
        print("\n✅ Database seeded successfully!")
        print("\nSample accounts:")
        print("  Employer: employer@techcorp.com / password123")
        print("  Job Seeker: john@example.com / password123")

if __name__ == "__main__":
    seed_database()
