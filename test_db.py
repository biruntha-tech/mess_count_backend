from database import SessionLocal
import models
import schemas

db = SessionLocal()
try:
    users = db.query(models.User).all()
    print(f"Found {len(users)} users.")
    for user in users:
        print(f"Validating user: {user.email}")
        try:
            schemas.UserResponse.model_validate(user)
            print("Validation successful!")
        except Exception as e:
            print(f"Validation failed for user {user.email}: {e}")
finally:
    db.close()
