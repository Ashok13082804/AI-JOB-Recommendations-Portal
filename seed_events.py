from app import app, db
from models import Event
from datetime import datetime, timedelta

def seed_events():
    with app.app_context():
        db.create_all()
        if Event.query.count() > 0:
            print("Events already exist, skipping seed.")
            return

        print("Seeding sample events...")
        
        # Current time for reference
        now = datetime.utcnow()

        events_data = [
            {
                "title": "Machine Learning Workshop 2024",
                "organizer": "AI Innovations Group",
                "description": "A comprehensive 2-day workshop on modern ML techniques using PyTorch and Scikit-learn. Suitable for developers with basic Python knowledge.",
                "event_type": "workshop",
                "is_internship": False,
                "location": "Bangalore",
                "url": "https://example.com/ml-workshop",
                "start_date": now + timedelta(days=10, hours=10),
                "end_date": now + timedelta(days=11, hours=17)
            },
            {
                "title": "Global Fintech Conference",
                "organizer": "Fintech Global",
                "description": "Discover the future of finance, blockchain, and digital banking at this international conference featuring speakers from top banks and startups.",
                "event_type": "conference",
                "is_internship": False,
                "location": "Online",
                "url": "https://example.com/fintech-conf",
                "start_date": now + timedelta(days=20, hours=9),
                "end_date": now + timedelta(days=22, hours=18)
            },
            {
                "title": "Summer Internship Fair 2025",
                "organizer": "Job Portal Support",
                "description": "Connect with top tech companies looking for summer interns. Open to all students and recent graduates.",
                "event_type": "internship_fair",
                "is_internship": True,
                "location": "Mumbai",
                "start_date": now + timedelta(days=15, hours=10),
                "end_date": now + timedelta(days=15, hours=16)
            },
            {
                "title": "Web Development Bootcamp",
                "organizer": "Fullstack Academy",
                "description": "Intensive workshop on React and Node.js for beginners.",
                "event_type": "workshop",
                "is_internship": False,
                "location": "Pune",
                "start_date": now + timedelta(days=5, hours=9),
                "end_date": now + timedelta(days=5, hours=17)
            }
        ]

        for data in events_data:
            event = Event(**data)
            db.session.add(event)

        db.session.commit()
        print("Events seeded successfully!")

if __name__ == "__main__":
    seed_events()
