import uuid
from database import SessionLocal
import models
from auth import get_password_hash
from datetime import date

def seed_database():
    db = SessionLocal()
    try:
        # Check if we already have data
        if db.query(models.Batch).first():
            print("Database already contains data! Skipping seed.")
            return

        print("Seeding database...")

        # 1. Create Batches
        batch1 = models.Batch(id=uuid.uuid4(), name="RCD 2026")
        batch2 = models.Batch(id=uuid.uuid4(), name="RCD 2027")
        db.add_all([batch1, batch2])
        db.commit()

        # 2. Create Messes
        mess1 = models.Mess(id=uuid.uuid4(), name="Chennai Mess", status="active")
        mess2 = models.Mess(id=uuid.uuid4(), name="Karaikudi Mess", status="active")
        db.add_all([mess1, mess2])
        db.commit()

        # 3. Create Admin User
        admin_user = models.User(
            id=uuid.uuid4(),
            name="Admin User",
            email="admin@example.com",
            phone="9999999999",
            hashed_password=get_password_hash("admin123"),
            role="admin",
            notification_enabled=True
        )

        # 4. Create Student User
        student_user = models.User(
            id=uuid.uuid4(),
            name="Student Biruntha",
            email="student@example.com",
            phone="8888888888",
            hashed_password=get_password_hash("student123"),
            role="student",
            batch_id=batch1.id,
            mess_id=mess1.id,
            notification_enabled=True
        )
        db.add_all([admin_user, student_user])
        db.commit()

        # 5. Create Weekly Menu for Mess 1
        menu1 = models.WeeklyMenu(
            id=uuid.uuid4(),
            mess_id=mess1.id,
            day="Monday",
            breakfast_item="Idli & Sambar",
            lunch_item="Rice & Chicken Curry",
            dinner_item="Chapathi & Dal"
        )
        db.add(menu1)
        
        # 6. Create a Food Submission for today
        submission = models.FoodSubmission(
            id=uuid.uuid4(),
            student_id=student_user.id,
            date=date.today(),
            mess_id=mess1.id,
            batch_id=batch1.id,
            breakfast=True,
            lunch=True,
            dinner=False,
            confirmed=False
        )
        db.add(submission)

        db.commit()
        print("Successfully seeded the database with test values!")
        
        print("\n--- TEST ACCOUNTS ---")
        print("Admin Login: admin@example.com / admin123")
        print("Student Login: student@example.com / student123")
        print("---------------------\n")

    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
