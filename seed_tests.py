from app import app, db
from models import PsychologicalTest, SkillTest
import json

def seed_tests():
    with app.app_context():
        db.create_all()
        if PsychologicalTest.query.count() > 0:
            print("Tests already exist, skipping seed.")
            return

        print("Seeding sample tests...")

        # Psychological Test
        psych_test = PsychologicalTest(
            title="Workplace Personality Assessment",
            description="Discover your professional strengths and ideal work environment.",
            questions_json=json.dumps([
                {
                    "text": "How do you handle high-pressure deadlines?",
                    "options": [
                        {"text": "I thrive and stay very organized", "value": 10},
                        {"text": "I manage but feel some stress", "value": 7},
                        {"text": "I prefer to avoid them if possible", "value": 4},
                        {"text": "I struggle significantly", "value": 2}
                    ]
                },
                {
                    "text": "What is your preferred communication style?",
                    "options": [
                        {"text": "Direct and concise", "value": 10},
                        {"text": "Collaborative and discussion-based", "value": 8},
                        {"text": "Mostly written/email", "value": 6},
                        {"text": "I prefer to follow instructions", "value": 4}
                    ]
                },
                {
                    "text": "How do you react to unexpected changes in project scope?",
                    "options": [
                        {"text": "I adapt quickly and look for solutions", "value": 10},
                        {"text": "I need some time to adjust", "value": 6},
                        {"text": "I find it very frustrating", "value": 3}
                    ]
                }
            ])
        )
        db.session.add(psych_test)

        # Skill Tests
        python_test = SkillTest(
            skill_name="Python Core",
            level="intermediate",
            duration_minutes=15,
            questions_json=json.dumps([
                {
                    "text": "What is the output of print(type([]) is list)?",
                    "options": {"A": "True", "B": "False", "C": "Error", "D": "None"},
                    "correct": "A"
                },
                {
                    "text": "Which of these is used to handle exceptions in Python?",
                    "options": {"A": "try-catch", "B": "try-except", "C": "do-while", "D": "throw-catch"},
                    "correct": "B"
                },
                {
                    "text": "How do you define a function in Python?",
                    "options": {"A": "func name():", "B": "new function name():", "C": "def name():", "D": "function name():"},
                    "correct": "C"
                }
            ])
        )
        db.session.add(python_test)

        react_test = SkillTest(
            skill_name="React.js",
            level="beginner",
            duration_minutes=10,
            questions_json=json.dumps([
                {
                    "text": "What hook is used to manage state in a functional component?",
                    "options": {"A": "useEffect", "B": "useState", "C": "useContext", "D": "useReducer"},
                    "correct": "B"
                },
                 {
                    "text": "What is the property used to pass data to a child component?",
                    "options": {"A": "State", "B": "Props", "C": "Data", "D": "Link"},
                    "correct": "B"
                }
            ])
        )
        db.session.add(react_test)

        db.session.commit()
        print("Tests seeded successfully!")

if __name__ == "__main__":
    seed_tests()
