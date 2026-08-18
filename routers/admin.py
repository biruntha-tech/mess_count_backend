from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import date, timedelta
import models, schemas, auth
from database import get_db

router = APIRouter(prefix="/api/admin", tags=["Admin"])

@router.get("/dashboard/stats", response_model=schemas.DashboardStatsResponse)
def get_dashboard_stats(current_user: models.User = Depends(auth.require_admin), db: Session = Depends(get_db)):
    total_students = db.query(models.User).filter(models.User.role == "student").count()
    today = date.today()
    today_submissions = db.query(models.FoodSubmission).filter(models.FoodSubmission.date == today).count()
    active_messes = db.query(models.Mess).filter(models.Mess.status == "active").count()
    
    return {
        "totalStudents": total_students,
        "todaySubmissions": today_submissions,
        "activeMesses": active_messes
    }

@router.get("/food-count", response_model=List[schemas.MessFoodCount])
def get_food_count(date_param: date = Query(..., alias="date"), current_user: models.User = Depends(auth.require_admin), db: Session = Depends(get_db)):
    messes = db.query(models.Mess).all()
    results = []
    for mess in messes:
        subs = db.query(models.FoodSubmission).filter(
            models.FoodSubmission.date == date_param,
            models.FoodSubmission.mess_id == mess.id
        ).all()
        
        bf_count = sum(1 for s in subs if s.breakfast)
        l_count = sum(1 for s in subs if s.lunch)
        d_count = sum(1 for s in subs if s.dinner)
        
        results.append({
            "mess_id": mess.id,
            "mess_name": mess.name,
            "breakfast_count": bf_count,
            "lunch_count": l_count,
            "dinner_count": d_count
        })
    return results

@router.get("/food-count/batch-wise", response_model=List[schemas.BatchFoodCount])
def get_batch_food_count(date_param: date = Query(..., alias="date"), current_user: models.User = Depends(auth.require_admin), db: Session = Depends(get_db)):
    batches = db.query(models.Batch).all()
    results = []
    for batch in batches:
        subs = db.query(models.FoodSubmission).filter(
            models.FoodSubmission.date == date_param,
            models.FoodSubmission.batch_id == batch.id
        ).all()
        
        bf_count = sum(1 for s in subs if s.breakfast)
        l_count = sum(1 for s in subs if s.lunch)
        d_count = sum(1 for s in subs if s.dinner)
        
        results.append({
            "batch_id": batch.id,
            "batch_name": batch.name,
            "breakfast_count": bf_count,
            "lunch_count": l_count,
            "dinner_count": d_count
        })
    return results

@router.get("/students/pending", response_model=List[schemas.UserResponse])
def get_pending_students(
    date_param: date = Query(..., alias="date"),
    mess_id: Optional[str] = None,
    batch_id: Optional[str] = None,
    current_user: models.User = Depends(auth.require_admin),
    db: Session = Depends(get_db)
):
    # Find all students
    query = db.query(models.User).filter(models.User.role == "student")
    if mess_id:
        query = query.filter(models.User.mess_id == mess_id)
    if batch_id:
        query = query.filter(models.User.batch_id == batch_id)
    all_students = query.all()
    
    # Find students who have submitted for this date
    submitted_student_ids = [
        sub.student_id for sub in db.query(models.FoodSubmission).filter(
            models.FoodSubmission.date == date_param
        ).all()
    ]
    
    pending_students = [s for s in all_students if s.id not in submitted_student_ids]
    return pending_students

@router.get("/attendance", response_model=List[schemas.AttendanceResponse])
def get_attendance(
    date_param: Optional[date] = Query(None, alias="date"),
    type: str = "daily", # daily, weekly, monthly
    student_id: Optional[str] = None,
    batch_id: Optional[str] = None,
    mess_id: Optional[str] = None,
    current_user: models.User = Depends(auth.require_admin),
    db: Session = Depends(get_db)
):
    query = db.query(models.Attendance)
    
    if type == "daily" and date_param:
        query = query.filter(models.Attendance.date == date_param)
    elif type == "weekly" and date_param:
        start_date = date_param - timedelta(days=date_param.weekday())
        end_date = start_date + timedelta(days=6)
        query = query.filter(models.Attendance.date >= start_date, models.Attendance.date <= end_date)
    elif type == "monthly" and date_param:
        query = query.filter(func.extract('month', models.Attendance.date) == date_param.month,
                             func.extract('year', models.Attendance.date) == date_param.year)
        
    if student_id:
        query = query.filter(models.Attendance.student_id == student_id)
        
    # to filter by batch/mess we need to join with User
    if batch_id or mess_id:
        query = query.join(models.User)
        if batch_id:
            query = query.filter(models.User.batch_id == batch_id)
        if mess_id:
            query = query.filter(models.User.mess_id == mess_id)
            
    return query.all()

@router.get("/students", response_model=List[schemas.UserResponse])
def get_students(current_user: models.User = Depends(auth.require_admin), db: Session = Depends(get_db)):
    return db.query(models.User).filter(models.User.role == "student").all()

# --- Batches CRUD ---
@router.get("/batches", response_model=List[schemas.BatchResponse])
def get_batches(current_user: models.User = Depends(auth.require_admin), db: Session = Depends(get_db)):
    return db.query(models.Batch).all()

@router.post("/batches", response_model=schemas.BatchResponse)
def create_batch(batch: schemas.BatchCreate, current_user: models.User = Depends(auth.require_admin), db: Session = Depends(get_db)):
    db_batch = models.Batch(name=batch.name)
    db.add(db_batch)
    db.commit()
    db.refresh(db_batch)
    return db_batch

@router.put("/batches/{batch_id}", response_model=schemas.BatchResponse)
def update_batch(batch_id: str, batch: schemas.BatchCreate, current_user: models.User = Depends(auth.require_admin), db: Session = Depends(get_db)):
    db_batch = db.query(models.Batch).filter(models.Batch.id == batch_id).first()
    if not db_batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    db_batch.name = batch.name
    db.commit()
    db.refresh(db_batch)
    return db_batch

@router.delete("/batches/{batch_id}")
def delete_batch(batch_id: str, current_user: models.User = Depends(auth.require_admin), db: Session = Depends(get_db)):
    db_batch = db.query(models.Batch).filter(models.Batch.id == batch_id).first()
    if not db_batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    db.delete(db_batch)
    db.commit()
    return {"message": "Batch deleted successfully"}

# --- Messes CRUD ---
@router.get("/messes", response_model=List[schemas.MessResponse])
def get_messes(current_user: models.User = Depends(auth.require_admin), db: Session = Depends(get_db)):
    return db.query(models.Mess).all()

@router.post("/messes", response_model=schemas.MessResponse)
def create_mess(mess: schemas.MessCreate, current_user: models.User = Depends(auth.require_admin), db: Session = Depends(get_db)):
    db_mess = models.Mess(name=mess.name, status=mess.status)
    db.add(db_mess)
    db.commit()
    db.refresh(db_mess)
    return db_mess

@router.put("/messes/{mess_id}", response_model=schemas.MessResponse)
def update_mess(mess_id: str, mess: schemas.MessCreate, current_user: models.User = Depends(auth.require_admin), db: Session = Depends(get_db)):
    db_mess = db.query(models.Mess).filter(models.Mess.id == mess_id).first()
    if not db_mess:
        raise HTTPException(status_code=404, detail="Mess not found")
    db_mess.name = mess.name
    db_mess.status = mess.status
    db.commit()
    db.refresh(db_mess)
    return db_mess

@router.put("/menu/{menu_row_id}", response_model=schemas.WeeklyMenuResponse)
def update_menu(menu_row_id: str, menu: schemas.WeeklyMenuCreate, current_user: models.User = Depends(auth.require_admin), db: Session = Depends(get_db)):
    db_menu = db.query(models.WeeklyMenu).filter(models.WeeklyMenu.id == menu_row_id).first()
    if not db_menu:
        raise HTTPException(status_code=404, detail="Menu row not found")
    db_menu.breakfast_item = menu.breakfast_item
    db_menu.lunch_item = menu.lunch_item
    db_menu.dinner_item = menu.dinner_item
    db.commit()
    db.refresh(db_menu)
    return db_menu
