import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import os
from pywebpush import webpush, WebPushException
import models, schemas, auth
from database import get_db

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])
admin_router = APIRouter(prefix="/api/admin/notifications", tags=["Admin Notifications"])

VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY", "dev_vapid_private_key")
VAPID_CLAIMS = {"sub": "mailto:admin@messcount.local"}

def send_web_push(subscription: models.PushSubscription, payload: str):
    try:
        webpush(
            subscription_info={
                "endpoint": subscription.endpoint,
                "keys": {
                    "p256dh": subscription.p256dh,
                    "auth": subscription.auth
                }
            },
            data=payload,
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims=VAPID_CLAIMS
        )
    except WebPushException as ex:
        print("I'm sorry, Dave, I'm afraid I can't do that: {}", repr(ex))
        # Log exception or clean up invalid subscriptions
        pass

@router.post("/subscribe")
def subscribe(sub_data: schemas.PushSubscriptionCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    db_sub = db.query(models.PushSubscription).filter(
        models.PushSubscription.user_id == current_user.id,
        models.PushSubscription.endpoint == sub_data.endpoint
    ).first()
    
    if not db_sub:
        db_sub = models.PushSubscription(
            user_id=current_user.id,
            endpoint=sub_data.endpoint,
            p256dh=sub_data.keys.p256dh,
            auth=sub_data.keys.auth
        )
        db.add(db_sub)
        db.commit()
    return {"message": "Subscribed successfully"}

@router.put("/settings")
def update_notification_settings(settings: schemas.NotificationSettingsUpdate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    current_user.notification_enabled = settings.enabled
    db.commit()
    return {"message": "Notification settings updated"}

@admin_router.post("/send")
def send_reminder(payload: str = Query(..., description="Message to send"), current_user: models.User = Depends(auth.require_admin), db: Session = Depends(get_db)):
    subscriptions = db.query(models.PushSubscription).join(models.User).filter(models.User.notification_enabled == True).all()
    count = 0
    for sub in subscriptions:
        send_web_push(sub, payload)
        count += 1
    return {"message": f"Sent reminder to {count} devices"}

@admin_router.post("/remind-pending")
def remind_pending(date_param: str = Query(..., alias="date"), payload: str = Query(..., description="Message to send"), current_user: models.User = Depends(auth.require_admin), db: Session = Depends(get_db)):
    # Find users who haven't submitted
    submitted_student_ids = [
        sub.student_id for sub in db.query(models.FoodSubmission).filter(
            models.FoodSubmission.date == date_param
        ).all()
    ]
    
    pending_users = db.query(models.User).filter(
        models.User.role == "student",
        models.User.id.not_in(submitted_student_ids),
        models.User.notification_enabled == True
    ).all()
    
    pending_user_ids = [u.id for u in pending_users]
    
    subscriptions = db.query(models.PushSubscription).filter(
        models.PushSubscription.user_id.in_(pending_user_ids)
    ).all()
    
    count = 0
    for sub in subscriptions:
        send_web_push(sub, payload)
        count += 1
    return {"message": f"Sent reminder to {count} pending devices"}

@admin_router.post("/remind-batch")
def remind_batch(batch_id: uuid.UUID, payload: str = Query(..., description="Message to send"), current_user: models.User = Depends(auth.require_admin), db: Session = Depends(get_db)):
    subscriptions = db.query(models.PushSubscription).join(models.User).filter(
        models.User.batch_id == batch_id,
        models.User.notification_enabled == True
    ).all()
    count = 0
    for sub in subscriptions:
        send_web_push(sub, payload)
        count += 1
    return {"message": f"Sent reminder to {count} devices in batch"}

@admin_router.post("/remind-mess")
def remind_mess(mess_id: uuid.UUID, payload: str = Query(..., description="Message to send"), current_user: models.User = Depends(auth.require_admin), db: Session = Depends(get_db)):
    subscriptions = db.query(models.PushSubscription).join(models.User).filter(
        models.User.mess_id == mess_id,
        models.User.notification_enabled == True
    ).all()
    count = 0
    for sub in subscriptions:
        send_web_push(sub, payload)
        count += 1
    return {"message": f"Sent reminder to {count} devices in mess"}
