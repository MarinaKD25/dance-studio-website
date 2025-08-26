# Импорт необходимых модулей
from typing import Optional, List
from sqlmodel import Field, SQLModel, select, UniqueConstraint, Relationship
from datetime import (
    date,
    datetime,
    time,
)
from pydantic import EmailStr, constr, validator
from enum import Enum
from sqlmodel import Session, create_engine
from sqlalchemy import text

# Настройка подключения к базе данных
engine = create_engine(
    'postgresql://postgres:123456789@localhost:5432/postgres',
    echo=True  # Включаем логирование SQL-запросов для отладки
)

# Перечисления для полей с ограниченным набором значений
class Gender(str, Enum):
    """Перечисление для пола"""
    MALE = "M"
    FEMALE = "F"

class SubscriptionStatus(str, Enum):
    """Перечисление для статуса подписки"""
    ACTIVE = "active"
    EXPIRED = "expired"

class UserRole(str, Enum):
    """Перечисление для ролей пользователей"""
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"

class PaymentMethod(str, Enum):
    """Перечисление для методов оплаты"""
    CARD = "card"
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"

class PaymentStatus(str, Enum):
    """Перечисление для статусов платежа"""
    COMPLETED = "completed"
    PENDING = "pending"
    FAILED = "failed"

class AttendanceStatus(str, Enum):
    """Перечисление для статусов посещаемости"""
    REGISTERED = "Записан"
    PRESENT = "Присутствовал"

# Модели таблиц базы данных
class Users(SQLModel, table=True):
    __tablename__ = 'users'
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True)
    password_hash: str
    role: UserRole
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Relationships
    student: Optional["Students"] = Relationship(back_populates="user")
    teacher: Optional["Teachers"] = Relationship(back_populates="user")

class Students(SQLModel, table=True):
    __tablename__ = 'students'
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    full_name: str = Field(max_length=50)
    date_of_birth: date  
    gender: Gender
    phone: str = Field(max_length=12)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Relationships
    user: Users = Relationship(back_populates="student")
    subscriptions: List["Subscriptions"] = Relationship(back_populates="student")
    attendance: List["Attendance"] = Relationship(back_populates="student_attendance")  # Обновлено

    @validator('date_of_birth')
    def validate_date_of_birth(cls, v):
        if v > date.today():
            raise ValueError('Date of birth cannot be in the future')
        if v < date(1900, 1, 1):
            raise ValueError('Date of birth cannot be before 1900')
        return v

class Payments(SQLModel, table=True):
    __tablename__ = 'payments'
    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="students.id")
    amount: float = Field(gt=0)
    payment_date: datetime = Field(default_factory=datetime.now)
    payment_method: PaymentMethod
    status: PaymentStatus = Field(default=PaymentStatus.COMPLETED)

    # Обратная связь
    subscriptions: List["Subscriptions"] = Relationship(back_populates="payment_method")

    @validator('payment_method')
    def validate_payment_method(cls, v):
        if not isinstance(v, PaymentMethod):
            raise ValueError(f'Payment method must be one of: {", ".join([m.value for m in PaymentMethod])}')
        return v

class Teachers(SQLModel, table=True):
    """Модель таблицы преподавателей"""
    __tablename__ = 'teachers'
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    full_name: str = Field(max_length=50)
    experience: int = Field(ge=0)  # Проверка в SQL: CHECK (experience >= 0)
    specialization: str = Field(max_length=20)
    phone: str = Field(max_length=12)  # Проверка формата в SQL: CHECK (phone ~ '^\+7\d{10}$')
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Relationships
    user: Users = Relationship(back_populates="teacher")
    classes: List["Classes"] = Relationship(back_populates="teacher")
    attendance: List["Attendance"] = Relationship(back_populates="teacher_attendance")  # Обновлено

    @validator('experience')
    def validate_experience(cls, v):
        if v > 50:
            raise ValueError('Experience cannot exceed 50 years')
        return v

class Subscriptions(SQLModel, table=True):
    __tablename__ = 'subscriptions'
    id: Optional[int] = Field(default=None, primary_key=True)
    start_date: date = Field(default_factory=date.today)
    end_date: date = Field(default_factory=lambda: date.today().replace(month=date.today().month + 1))
    number_of_classes: int = Field(default=8, ge=0, le=16)
    remaining_classes: int = Field(default=8, ge=0, le=16)
    status: SubscriptionStatus
    student_id: int = Field(foreign_key="students.id")
    payment_id: int = Field(foreign_key="payments.id")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # Явно указываем связь с Students
    student: Optional["Students"] = Relationship(back_populates="subscriptions")
    payment_method: Optional["Payments"] = Relationship(back_populates="subscriptions")

    @validator('end_date')
    def validate_end_date(cls, v, values):
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('End date cannot be before start date')
        return v

class Halls(SQLModel, table=True):
    """Модель таблицы залов"""
    __tablename__ = 'halls'
    id: Optional[int] = Field(default=None, primary_key=True)
    hall_number: int = Field(unique=True)
    capacity: int = Field(gt=0)  # Проверка в SQL: CHECK (capacity > 0)
    description: str = Field(max_length=200, default="")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    @validator('capacity')
    def validate_capacity(cls, v):
        if v > 100:
            raise ValueError('Capacity cannot exceed 100')
        return v

class Classes(SQLModel, table=True):
    """Модель таблицы занятий"""
    __tablename__ = 'classes'
    id: Optional[int] = Field(default=None, primary_key=True)
    time: time
    type: str = Field(max_length=18)
    hall_id: Optional[int] = Field(foreign_key="halls.id")
    teacher_id: int = Field(foreign_key="teachers.id")
    date: date
    current_capacity: int = Field(default=0, ge=0)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    teacher: "Teachers" = Relationship(back_populates="classes")
    attendance: List["Attendance"] = Relationship(back_populates="class_attendance")

    @validator('time')
    def validate_time(cls, v):
        if v is None:
            raise ValueError('Время не может быть пустым')
        return v

    @validator('current_capacity')
    def validate_current_capacity(cls, v, values):
        if 'hall_id' in values and values['hall_id'] is not None:
            with Session(engine) as session:
                hall = session.get(Halls, values['hall_id'])
                if hall and v > hall.capacity:
                    raise ValueError('Текущая вместимость не может превышать вместимость зала')
        return v

class Attendance(SQLModel, table=True):
    """Модель таблицы посещаемости"""
    __tablename__ = 'attendance'
    id: Optional[int] = Field(default=None, primary_key=True)
    presence: AttendanceStatus = Field(default=AttendanceStatus.REGISTERED)
    student_id: Optional[int] = Field(foreign_key="students.id")
    class_id: Optional[int] = Field(foreign_key="classes.id")
    teacher_id: Optional[int] = Field(foreign_key="teachers.id")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    student_attendance: Optional["Students"] = Relationship(back_populates="attendance")
    class_attendance: Optional["Classes"] = Relationship(back_populates="attendance")
    teacher_attendance: Optional["Teachers"] = Relationship(back_populates="attendance")

    @validator('presence')
    def validate_presence(cls, v):
        if v not in [status.value for status in AttendanceStatus]:
            raise ValueError(f'Presence must be one of: {", ".join([status.value for status in AttendanceStatus])}')
        return v

class Admins(SQLModel, table=True):
    """Модель таблицы администраторов"""
    __tablename__ = 'admins'
 
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")  # Обязательное поле
    full_name: str = Field(max_length=50)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

   

