from typing import Optional
from datetime import date, datetime, timedelta
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlmodel import SQLModel, Field
from backend.ll1 import SubscriptionStatus

class Subscriptions(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="students.id")
    status: SubscriptionStatus = Field(default=SubscriptionStatus.ACTIVE)
    number_of_classes: int = Field(default=8)
    remaining_classes: int = Field(default=8)
    start_date: date = Field(default_factory=date.today)
    end_date: date = Field(default_factory=lambda: date.today() + timedelta(days=30))
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now) 