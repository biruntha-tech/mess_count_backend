from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import date, datetime
import uuid

# --- Users ---

class UserBase(BaseModel):
    name: str
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    role: str
    batch_id: Optional[uuid.UUID] = None
    mess_id: Optional[uuid.UUID] = None
    notification_enabled: bool = True

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: uuid.UUID

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    batch_id: Optional[uuid.UUID] = None
    mess_id: Optional[uuid.UUID] = None
    notification_enabled: Optional[bool] = None
    password: Optional[str] = None

# --- Batches ---

class BatchBase(BaseModel):
    name: str

class BatchCreate(BatchBase):
    pass

class BatchResponse(BatchBase):
    id: uuid.UUID

    class Config:
        from_attributes = True

# --- Messes ---

class MessBase(BaseModel):
    name: str
    status: str

class MessCreate(MessBase):
    pass

class MessResponse(MessBase):
    id: uuid.UUID

    class Config:
        from_attributes = True

# --- Weekly Menu ---

class WeeklyMenuBase(BaseModel):
    day: str
    breakfast_item: str
    lunch_item: str
    dinner_item: str

class WeeklyMenuCreate(WeeklyMenuBase):
    pass

class WeeklyMenuUpdate(BaseModel):
    day: Optional[str] = None
    breakfast_item: Optional[str] = None
    lunch_item: Optional[str] = None
    dinner_item: Optional[str] = None


class WeeklyMenuResponse(WeeklyMenuBase):
    id: uuid.UUID
    mess_id: uuid.UUID

    class Config:
        from_attributes = True

# --- Food Submissions ---

class FoodSubmissionBase(BaseModel):
    date: date
    breakfast: bool
    lunch: bool
    dinner: bool
    confirmed: bool = False

class FoodSubmissionCreate(FoodSubmissionBase):
    pass

class FoodSubmissionUpdate(BaseModel):
    breakfast: Optional[bool] = None
    lunch: Optional[bool] = None
    dinner: Optional[bool] = None
    confirmed: Optional[bool] = None

class FoodSubmissionResponse(FoodSubmissionBase):
    id: uuid.UUID
    student_id: uuid.UUID
    mess_id: uuid.UUID
    batch_id: uuid.UUID
    submitted_at: datetime
    confirmed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# --- Attendance ---

class AttendanceBase(BaseModel):
    date: date
    status: str

class AttendanceResponse(AttendanceBase):
    id: uuid.UUID
    student_id: uuid.UUID

    class Config:
        from_attributes = True

# --- Auth ---

class Token(BaseModel):
    token: str
    user: UserResponse

class LoginRequest(BaseModel):
    email: str
    password: str
    role: str

# --- Notifications ---
class SubscriptionKeys(BaseModel):
    p256dh: str
    auth: str

class PushSubscriptionCreate(BaseModel):
    endpoint: str
    keys: SubscriptionKeys

class NotificationSettingsUpdate(BaseModel):
    enabled: bool

# --- Admin Dashboard Stats ---

class DashboardStatsResponse(BaseModel):
    totalStudents: int
    todaySubmissions: int
    activeMesses: int

class MessFoodCount(BaseModel):
    mess_id: uuid.UUID
    mess_name: str
    breakfast_count: int
    lunch_count: int
    dinner_count: int

class BatchFoodCount(BaseModel):
    batch_id: uuid.UUID
    batch_name: str
    breakfast_count: int
    lunch_count: int
    dinner_count: int
