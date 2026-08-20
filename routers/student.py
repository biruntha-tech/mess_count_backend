import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, datetime
import os
import models, schemas, auth
from database import get_db

router = APIRouter(prefix="/api/student", tags=["Student"])

def is_past_deadline():
    deadline_hour = int(os.getenv("SUBMISSION_DEADLINE_HOUR", "20"))
    now = datetime.now()
    if now.hour >= deadline_hour:
        return True
    return False

@router.get("/submissions/today", response_model=schemas.FoodSubmissionResponse)
def get_today_submission(date_param: date, current_user: models.User = Depends(auth.require_student), db: Session = Depends(get_db)):
    submission = db.query(models.FoodSubmission).filter(
        models.FoodSubmission.student_id == current_user.id,
        models.FoodSubmission.date == date_param
    ).first()
    
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found for today")
    return submission

@router.post("/submissions", response_model=schemas.FoodSubmissionResponse)
def create_submission(submission: schemas.FoodSubmissionCreate, current_user: models.User = Depends(auth.require_student), db: Session = Depends(get_db)):
    if is_past_deadline():
        raise HTTPException(status_code=400, detail="Deadline has passed for submissions")
        
    db_submission = db.query(models.FoodSubmission).filter(
        models.FoodSubmission.student_id == current_user.id,
        models.FoodSubmission.date == submission.date
    ).first()
    
    if db_submission:
        db_submission.breakfast = submission.breakfast
        db_submission.lunch = submission.lunch
        db_submission.dinner = submission.dinner
        db_submission.confirmed = submission.confirmed
        if submission.confirmed:
            db_submission.confirmed_at = datetime.utcnow()
    else:
        db_submission = models.FoodSubmission(
            student_id=current_user.id,
            date=submission.date,
            mess_id=current_user.mess_id,
            batch_id=current_user.batch_id,
            breakfast=submission.breakfast,
            lunch=submission.lunch,
            dinner=submission.dinner,
            confirmed=submission.confirmed,
            confirmed_at=datetime.utcnow() if submission.confirmed else None
        )
        db.add(db_submission)
        
    db.commit()
    db.refresh(db_submission)
    return db_submission

@router.put("/submissions/{submission_id}", response_model=schemas.FoodSubmissionResponse)
def edit_submission(submission_id: uuid.UUID, submission_update: schemas.FoodSubmissionUpdate, current_user: models.User = Depends(auth.require_student), db: Session = Depends(get_db)):
    db_submission = db.query(models.FoodSubmission).filter(
        models.FoodSubmission.id == submission_id,
        models.FoodSubmission.student_id == current_user.id
    ).first()
    
    if not db_submission:
        raise HTTPException(status_code=404, detail="Submission not found")
        
    if is_past_deadline():
        raise HTTPException(status_code=400, detail="Deadline has passed, modifications are not allowed")

    if submission_update.breakfast is not None:
        db_submission.breakfast = submission_update.breakfast
    if submission_update.lunch is not None:
        db_submission.lunch = submission_update.lunch
    if submission_update.dinner is not None:
        db_submission.dinner = submission_update.dinner
    if submission_update.confirmed is not None:
        db_submission.confirmed = submission_update.confirmed
        if submission_update.confirmed:
            db_submission.confirmed_at = datetime.utcnow()

    db.commit()
    db.refresh(db_submission)
    return db_submission

@router.get("/submissions/history", response_model=list[schemas.FoodSubmissionResponse])
def get_submission_history(current_user: models.User = Depends(auth.require_student), db: Session = Depends(get_db)):
    return db.query(models.FoodSubmission).filter(
        models.FoodSubmission.student_id == current_user.id
    ).order_by(models.FoodSubmission.date.desc()).all()

@router.get("/messes/{mess_id}/menu", response_model=list[schemas.WeeklyMenuResponse])
def get_mess_menu(mess_id: uuid.UUID, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    return db.query(models.WeeklyMenu).filter(models.WeeklyMenu.mess_id == mess_id).all()
