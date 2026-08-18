import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey, Date, DateTime, Time, Uuid

from sqlalchemy.orm import relationship
from database import Base
import datetime

class Batch(Base):
    __tablename__ = "batches"
    
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, index=True) # e.g., RCD 1
    
    users = relationship("User", back_populates="batch")
    submissions = relationship("FoodSubmission", back_populates="batch")


class Mess(Base):
    __tablename__ = "messes"
    
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, index=True) # Chennai or Karaikudi
    status = Column(String, default="active") # active, inactive
    
    users = relationship("User", back_populates="mess")
    menus = relationship("WeeklyMenu", back_populates="mess")
    submissions = relationship("FoodSubmission", back_populates="mess")


class User(Base):
    __tablename__ = "users"
    
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    phone = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String) # student, admin
    batch_id = Column(Uuid(as_uuid=True), ForeignKey("batches.id"), nullable=True)
    mess_id = Column(Uuid(as_uuid=True), ForeignKey("messes.id"), nullable=True)
    notification_enabled = Column(Boolean, default=True)
    
    batch = relationship("Batch", back_populates="users")
    mess = relationship("Mess", back_populates="users")
    submissions = relationship("FoodSubmission", back_populates="student")
    attendance_records = relationship("Attendance", back_populates="student")
    push_subscriptions = relationship("PushSubscription", back_populates="user")


class WeeklyMenu(Base):
    __tablename__ = "weekly_menus"
    
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mess_id = Column(Uuid(as_uuid=True), ForeignKey("messes.id"))
    day = Column(String) # Monday, Tuesday, etc.
    breakfast_item = Column(String)
    lunch_item = Column(String)
    dinner_item = Column(String)
    
    mess = relationship("Mess", back_populates="menus")


class FoodSubmission(Base):
    __tablename__ = "food_submissions"
    
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(Uuid(as_uuid=True), ForeignKey("users.id"))
    date = Column(Date)
    mess_id = Column(Uuid(as_uuid=True), ForeignKey("messes.id"))
    batch_id = Column(Uuid(as_uuid=True), ForeignKey("batches.id"))
    breakfast = Column(Boolean, default=False)
    lunch = Column(Boolean, default=False)
    dinner = Column(Boolean, default=False)
    confirmed = Column(Boolean, default=False)
    submitted_at = Column(DateTime, default=datetime.datetime.utcnow)
    confirmed_at = Column(DateTime, nullable=True)
    
    student = relationship("User", back_populates="submissions")
    mess = relationship("Mess", back_populates="submissions")
    batch = relationship("Batch", back_populates="submissions")


class Attendance(Base):
    __tablename__ = "attendance"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    date = Column(Date)
    status = Column(String) # present, absent, not_submitted
    
    student = relationship("User", back_populates="attendance_records")


class PushSubscription(Base):
    __tablename__ = "push_subscriptions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    endpoint = Column(String)
    p256dh = Column(String)
    auth = Column(String)
    
    user = relationship("User", back_populates="push_subscriptions")
