# Импорт необходимых модулей
from typing import Union, List, Optional, Dict, Any
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi import FastAPI, HTTPException, Depends, status, Header, Body
from fastapi.middleware.cors import CORSMiddleware
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import os
import jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, validator, Field
from sqlmodel import Session, select, and_
from ll1 import (
    Students, Teachers, Classes, Halls, Attendance, AttendanceStatus,Payments, Subscriptions,
    Gender, SubscriptionStatus, engine, Admins, Users, UserRole,PaymentMethod, PaymentStatus
)
from requests import (
    get_student_by_email, get_active_subscriptions, get_class_schedule,
    get_available_classes, enroll_student_in_class, mark_attendance,
    get_teacher_schedule, get_attendance_statistics, get_student_attendance,
    get_class_attendance, create_payment, create_subscription,
    get_all_teachers, get_all_halls, create_class
)
import bcrypt
from pydantic import ValidationError


# Создание экземпляра FastAPI приложения
app = FastAPI()  # Отключаем стандартный docs

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8081", "http://127.0.0.1:8081", "http://192.168.0.3:8081", "http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Конфигурация JWT
SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is not set in environment")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Модели ответов
class ClassResponse(BaseModel):
    id: int
    time: str
    type: str
    date: date
    current_capacity: int
    hall_number: int
    hall_capacity: int
    teacher_name: str
    formatted_date: str
    formatted_time: str
    teacher_id: int
    hall_id: int

    class Config:
        orm_mode = True

    @validator('formatted_date', 'formatted_time', pre=True)
    def format_datetime(cls, v, values):
        if 'date' in values:
            date = values['date']
            if isinstance(date, datetime):
                return {
                    'formatted_date': date.strftime('%d.%m.%Y'),
                    'formatted_time': date.strftime('%H:%M')
                }
        return v

class StudentResponse(BaseModel):
    id: int
    full_name: str
    email: str
    phone: str
    date_of_birth: date
    gender: Gender

class TeacherResponse(BaseModel):
    id: int
    full_name: str
    email: str
    phone: str
    experience: int
    specialization: str

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str

class LoginRequest(BaseModel):
    email: str
    password: str

class CreateClassRequest(BaseModel):
    time: str
    type: str
    hall_id: int
    teacher_id: int
    date: date

class SubscriptionResponse(BaseModel):
    id: int
    start_date: date
    end_date: date
    number_of_classes: int
    remaining_classes: int
    status: SubscriptionStatus
    student_id: int
    payment_id: int

    class Config:
        orm_mode = True

class UpdateClassRequest(BaseModel):
    time: str
    type: str
    hall_id: int
    teacher_id: int
    date: date

class CreateTeacherRequest(BaseModel):
    full_name: str
    email: str
    phone: str
    experience: int
    specialization: str
    password: str

class UpdateTeacherRequest(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    experience: Optional[int] = None
    specialization: Optional[str] = None
    password: Optional[str] = None

class CreateStudentRequest(BaseModel):
    full_name: str
    email: str
    phone: str
    date_of_birth: date
    gender: Gender
    password: str

class UpdateStudentRequest(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[Gender] = None
    password: Optional[str] = None

class AttendanceResponse(BaseModel):
    id: int
    presence: str
    student_id: int
    class_id: int
    teacher_id: int
    student_name: str
    class_: ClassResponse

    class Config:
        orm_mode = True

class UpdateAttendanceRequest(BaseModel):
    presence: str

class CreatePaymentAndSubscriptionRequest(BaseModel):
    student_id: int
    amount: float
    payment_method: PaymentMethod = PaymentMethod.CARD
    number_of_classes: int
    start_date: date = Field(default_factory=date.today)

    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be greater than 0')
        return v

    @validator('number_of_classes')
    def validate_number_of_classes(cls, v):
        if v <= 0:
            raise ValueError('Number of classes must be greater than 0')
        if v > 16:
            raise ValueError('Number of classes cannot exceed 16')
        return v

class PaymentAndSubscriptionResponse(BaseModel):
    payment: Payments
    subscription: Subscriptions

    class Config:
        orm_mode = True

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str):
    return pwd_context.hash(password)

def get_user(email: str):
    with Session(engine) as session:
        statement = select(Users).where(Users.email == email)
        return session.exec(statement).first()

def authenticate_user(email: str, password: str):
    user = get_user(email)
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Header(...)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Неверные учетные данные")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Неверные учетные данные")
    
    with Session(engine) as session:
        user = session.exec(select(Users).where(Users.email == email)).first()
        if user is None:
            raise HTTPException(status_code=401, detail="Пользователь не найден")
        return user

@app.post("/login", response_model=Token)
async def login(login_data: LoginRequest):
    """Эндпоинт для входа в систему"""
    print(f"Attempting login for user: {login_data.email}")
    
    try:
        user = authenticate_user(login_data.email, login_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "message": "Ошибка входа",
                    "errors": ["Неверный email или пароль"]
                },
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email, "role": user.role},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "role": user.role
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error during authentication: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Ошибка авторизации",
                "errors": ["Произошла внутренняя ошибка при попытке входа"]
            }
        )

@app.get("/users/me")
async def read_users_me(current_user: Users = Depends(get_current_user)):
    """Получение информации о текущем пользователе"""
    try:
        with Session(engine) as session:
            if current_user.role == UserRole.STUDENT:
                student = session.exec(select(Students).where(Students.user_id == current_user.id)).first()
                if not student:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail={
                            "message": "Профиль не найден",
                            "errors": ["Профиль студента не найден в системе"]
                        }
                    )
                return {
                    "id": current_user.id,
                    "email": current_user.email,
                    "role": current_user.role,
                    "name": student.full_name,
                    "student_id": student.id
                }
            elif current_user.role == UserRole.TEACHER:
                teacher = session.exec(select(Teachers).where(Teachers.user_id == current_user.id)).first()
                if not teacher:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail={
                            "message": "Профиль не найден",
                            "errors": ["Профиль преподавателя не найден в системе"]
                        }
                    )
                return {
                    "id": current_user.id,
                    "email": current_user.email,
                    "role": current_user.role,
                    "name": teacher.full_name,
                    "teacher_id": teacher.id
                }
            elif current_user.role == UserRole.ADMIN:
                admin = session.exec(select(Admins).where(Admins.user_id == current_user.id)).first()
                if not admin:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail={
                            "message": "Профиль не найден",
                            "errors": ["Профиль администратора не найден в системе"]
                        }
                    )
                return {
                    "id": current_user.id,
                    "email": current_user.email,
                    "role": current_user.role,
                    "name": admin.full_name
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "message": "Неизвестная роль",
                        "errors": ["Роль пользователя не определена в системе"]
                    }
                )
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error in read_users_me: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Ошибка получения данных пользователя",
                "errors": [
                    "Произошла ошибка при получении данных профиля",
                    "Пожалуйста, попробуйте позже или обратитесь в поддержку"
                ]
            }
        )

# Эндпоинты для работы с классами (расписанием)
@app.get("/classes/", response_model=List[ClassResponse])
def get_classes(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    dance_type: Optional[str] = None,
    teacher_id: Optional[int] = None
):
    """Получение расписания на текущую и следующую неделю с фильтрацией"""
    try:
        # Если даты не указаны, используем текущую дату и +14 дней
        if not start_date:
            start_date = date.today()
        if not end_date:
            end_date = start_date + timedelta(days=14)

        print(f"Получение занятий с {start_date} по {end_date}")
        with Session(engine) as session:
            query = (
                select(
                    Classes,
                    Halls.hall_number,
                    Halls.capacity.label("hall_capacity"),
                    Teachers.full_name.label("teacher_name"),
                    Teachers.specialization,
                    Teachers.id.label("teacher_id"),
                    Halls.id.label("hall_id")
                )
                .join(Halls, Classes.hall_id == Halls.id)
                .join(Teachers, Classes.teacher_id == Teachers.id)
                .where(
                    Classes.date >= start_date,
                    Classes.date <= end_date
                )
                .order_by(Classes.date, Classes.time)
            )
            
            if dance_type:
                query = query.where(Classes.type == dance_type)
            if teacher_id:
                query = query.where(Classes.teacher_id == teacher_id)
                
            classes = session.exec(query).all()
            print(f"Найдено занятий: {len(classes)}")
            
            result = []
            for cls, hall_number, hall_capacity, teacher_name, specialization, teacher_id, hall_id in classes:
                try:
                    # Форматируем дату и время
                    formatted_date = cls.date.strftime('%d.%m.%Y')
                    formatted_time = cls.time.strftime('%H:%M')
                    day_of_week = cls.date.strftime('%A')
                    
                    # Получаем русское название дня недели
                    russian_days = {
                        'Monday': 'Понедельник',
                        'Tuesday': 'Вторник',
                        'Wednesday': 'Среда',
                        'Thursday': 'Четверг',
                        'Friday': 'Пятница',
                        'Saturday': 'Суббота',
                        'Sunday': 'Воскресенье'
                    }
                    russian_day_of_week = russian_days.get(day_of_week, day_of_week)
                    
                    class_data = {
                        "id": cls.id,
                        "time": cls.time.strftime('%H:%M:%S'),
                        "type": cls.type,
                        "date": cls.date,
                        "current_capacity": cls.current_capacity,
                        "hall_number": hall_number,
                        "hall_capacity": hall_capacity,
                        "teacher_name": teacher_name,
                        "specialization": specialization,
                        "remaining_slots": hall_capacity - cls.current_capacity,
                        "formatted_date": formatted_date,
                        "formatted_time": formatted_time,
                        "day_of_week": russian_day_of_week,
                        "teacher_id": teacher_id,
                        "hall_id": hall_id
                    }
                    result.append(ClassResponse(**class_data))
                except Exception as e:
                    print(f"Ошибка при форматировании занятия {cls.id}: {str(e)}")
                    continue
            
            print(f"Возвращаем {len(result)} занятий")
            return result
    except Exception as e:
        print(f"Ошибка при получении расписания: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении расписания: {str(e)}"
        )

@app.get("/students/", response_model=List[StudentResponse])
def get_students():
    """Получение списка всех студентов с email"""
    with Session(engine) as session:
        query = (
            select(
                Students,
                Users.email
            )
            .join(Users, Students.user_id == Users.id)
        )
        students = session.exec(query).all()
        
        return [
            StudentResponse(
                id=student.id,
                full_name=student.full_name,
                email=email,
                phone=student.phone,
                date_of_birth=student.date_of_birth,
                gender=student.gender
            )
            for student, email in students
        ]

@app.get("/students/{student_id}", response_model=StudentResponse)
def get_student_by_id(student_id: int):
    """Получение информации о студенте по его ID"""
    with Session(engine) as session:
        query = (
            select(
                Students,
                Users.email
            )
            .join(Users, Students.user_id == Users.id)
            .where(Students.id == student_id)
        )
        result = session.exec(query).first()
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Студент не найден"
            )
            
        student, email = result
        return StudentResponse(
            id=student.id,
            full_name=student.full_name,
            email=email,
            phone=student.phone,
            date_of_birth=student.date_of_birth,
            gender=student.gender
        )

@app.get("/students/me", response_model=StudentResponse)
async def get_current_student(current_user: Users = Depends(get_current_user)):
    """Получение информации о текущем студенте"""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только для студентов"
        )
    
    with Session(engine) as session:
        query = (
            select(
                Students,
                Users.email
            )
            .join(Users, Students.user_id == Users.id)
            .where(Users.id == current_user.id)
        )
        result = session.exec(query).first()
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Студент не найден"
            )
            
        student, email = result
        return StudentResponse(
            id=student.id,
            full_name=student.full_name,
            email=email,
            phone=student.phone,
            date_of_birth=student.date_of_birth,
            gender=student.gender
        )

# Эндпоинты для преподавателей
@app.get("/teachers/", response_model=List[TeacherResponse])
def get_teachers():
    """Получение списка всех преподавателей с email"""
    with Session(engine) as session:
        query = select(
            Teachers,
            Users.email
        ).join(Users, Teachers.user_id == Users.id)
        
        teachers = session.exec(query).all()

    return [
            TeacherResponse(
                id=teacher.id,
                full_name=teacher.full_name,
                email=email,
                phone=teacher.phone,
                experience=teacher.experience,
                specialization=teacher.specialization
            )
            for teacher, email in teachers
        ]

# Эндпоинты для посещаемости
@app.get("/attendance/{class_id}", response_model=List[dict])
def get_class_attendance(class_id: int):
    """Получение посещаемости для конкретного класса"""
    with Session(engine) as session:
        query = (
            select(
                Attendance.id,
                Students.full_name,
                Users.email,
                Attendance.presence
            )
            .join(Students, Attendance.student_id == Students.id)
            .join(Users, Students.user_id == Users.id)
            .where(Attendance.class_id == class_id)
        )
        
        results = session.exec(query).all()
        return [
            {
                "id": att_id,
                "full_name": full_name,
                "email": email,
                "presence": presence
            }
            for att_id, full_name, email, presence in results
        ]

# Эндпоинты для администратора
@app.post("/classes/", response_model=ClassResponse)
def create_class(class_data: CreateClassRequest, current_user: Users = Depends(get_current_user)):
    """Создание нового занятия (только для администратора)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только для администраторов"
        )
    
    try:
        with Session(engine) as session:
            # Проверка существования зала и преподавателя
            hall = session.get(Halls, class_data.hall_id)
            teacher = session.get(Teachers, class_data.teacher_id)
            
            if not hall:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Зал не найден"
                )
            if not teacher:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Преподаватель не найден"
                )

            # Проверка на конфликты расписания
            existing_class = session.exec(
                select(Classes).where(
                    and_(
                        Classes.hall_id == class_data.hall_id,
                        Classes.date == class_data.date,
                        Classes.time == datetime.strptime(class_data.time, '%H:%M').time()
                    )
                )
            ).first()

            if existing_class:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Зал уже занят в это время"
                )

            # Создание нового занятия
            new_class = Classes(
                time=datetime.strptime(class_data.time, '%H:%M').time(),
                type=class_data.type,
                hall_id=class_data.hall_id,
                teacher_id=class_data.teacher_id,
                date=class_data.date,
                current_capacity=0
            )
            
            session.add(new_class)
            session.commit()
            session.refresh(new_class)

            # Форматируем данные для ответа
            formatted_date = new_class.date.strftime('%d.%m.%Y')
            formatted_time = new_class.time.strftime('%H:%M')
            day_of_week = new_class.date.strftime('%A')
            
            russian_days = {
                'Monday': 'Понедельник',
                'Tuesday': 'Вторник',
                'Wednesday': 'Среда',
                'Thursday': 'Четверг',
                'Friday': 'Пятница',
                'Saturday': 'Суббота',
                'Sunday': 'Воскресенье'
            }
            russian_day_of_week = russian_days.get(day_of_week, day_of_week)

            return ClassResponse(
                id=new_class.id,
                time=new_class.time.strftime('%H:%M:%S'),
                type=new_class.type,
                date=new_class.date,
                current_capacity=new_class.current_capacity,
                hall_number=hall.hall_number,
                hall_capacity=hall.capacity,
                teacher_name=teacher.full_name,
                specialization=teacher.specialization,
                remaining_slots=hall.capacity - new_class.current_capacity,
                formatted_date=formatted_date,
                formatted_time=formatted_time,
                day_of_week=russian_day_of_week,
                teacher_id=teacher.id,
                hall_id=hall.id
            )
    except Exception as e:
        print(f"Ошибка при создании занятия: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при создании занятия: {str(e)}"
        )

@app.get("/attendance/student/{student_id}", response_model=List[AttendanceResponse])
def get_student_attendance_endpoint(student_id: int):
    """Получение посещаемости студента"""
    try:
        with Session(engine) as session:
            # Получаем все записи о посещаемости для студента
            attendance_records = session.exec(
                select(Attendance)
                .where(Attendance.student_id == student_id)
            ).all()
            
            if not attendance_records:
                return []
            
            # Создаем список ответов
            response = []
            for record in attendance_records:
                # Получаем информацию о занятии
                class_info = session.get(Classes, record.class_id)
                if not class_info:
                    continue
                    
                # Получаем информацию о преподавателе
                teacher = session.get(Teachers, class_info.teacher_id)
                if not teacher:
                    continue
                    
                # Получаем информацию о зале
                hall = session.get(Halls, class_info.hall_id)
                if not hall:
                    continue
                    
                # Получаем информацию о студенте
                student = session.get(Students, record.student_id)
                
                response.append(AttendanceResponse(
                    id=record.id,
                    presence=record.presence,
                    student_id=record.student_id,
                    class_id=record.class_id,
                    teacher_id=record.teacher_id,
                    student_name=student.full_name if student else "Unknown",
                    class_=ClassResponse(
                        id=class_info.id,
                        time=class_info.time.strftime('%H:%M:%S'),
                        type=class_info.type,
                        date=class_info.date,
                        current_capacity=class_info.current_capacity,
                        hall_number=hall.hall_number,
                        hall_capacity=hall.capacity,
                        teacher_name=teacher.full_name,
                        formatted_date=class_info.date.strftime('%d.%m.%Y'),
                        formatted_time=class_info.time.strftime('%H:%M'),
                        teacher_id=class_info.teacher_id,
                        hall_id=class_info.hall_id
                    )
                ))
            
            return response
    except Exception as e:
        print(f"Error in get_student_attendance_endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting student attendance: {str(e)}"
        )

@app.get("/attendance/class/{class_id}", response_model=List[AttendanceResponse])
async def get_class_attendance_endpoint(class_id: int):
    """Получение списка записанных студентов на занятие"""
    with Session(engine) as session:
        # Получаем все записи о посещаемости для занятия
        attendances = session.exec(
            select(Attendance)
            .join(Students, Attendance.student_id == Students.id)
            .where(Attendance.class_id == class_id)
        ).all()

        result = []
        for attendance in attendances:
            student = session.get(Students, attendance.student_id)
            class_ = session.get(Classes, attendance.class_id)
            hall = session.get(Halls, class_.hall_id)
            teacher = session.get(Teachers, class_.teacher_id)
            if student and class_:
                result.append(AttendanceResponse(
                    id=attendance.id,
                    presence=attendance.presence,
                    student_id=attendance.student_id,
                    class_id=attendance.class_id,
                    teacher_id=attendance.teacher_id,
                    student_name=student.full_name,
                    class_=ClassResponse(
                        id=class_.id,
                        time=class_.time.strftime('%H:%M:%S'),
                        type=class_.type,
                        date=class_.date,
                        current_capacity=class_.current_capacity,
                        hall_number=hall.hall_number,
                        hall_capacity=hall.capacity,
                        teacher_name=teacher.full_name,
                        specialization=teacher.specialization,
                        remaining_slots=hall.capacity - class_.current_capacity,
                        formatted_date=class_.date.strftime('%d.%m.%Y'),
                        formatted_time=class_.time.strftime('%H:%M'),
                        day_of_week=class_.date.strftime('%A'),
                        teacher_id=class_.teacher_id,
                        hall_id=class_.hall_id
                    )
                ))

        return result

# Эндпоинты для залов
@app.get("/halls/", response_model=List[Halls])
def read_halls():
    """Получение списка всех залов"""
    return get_all_halls()

@app.post("/classes/{class_id}/enroll", response_model=Dict[str, Any])
async def enroll_in_class(
    class_id: int,
    current_user: Users = Depends(get_current_user)
):
    """Запись студента на занятие"""
    with Session(engine) as session:
        # Проверяем, что пользователь является студентом
        if current_user.role != UserRole.STUDENT:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Только студенты могут записываться на занятия"
            )

        # Получаем студента
        student = session.exec(
            select(Students).where(Students.user_id == current_user.id)
        ).first()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Студент не найден"
            )

        # Получаем занятие
        class_ = session.get(Classes, class_id)
        if not class_:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Занятие не найдено"
            )

        # Получаем информацию о зале
        hall = session.get(Halls, class_.hall_id)
        if not hall:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Зал не найден"
            )

        # Проверяем, не заполнен ли зал
        if class_.current_capacity >= hall.capacity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Зал уже заполнен"
            )

        # Проверяем, не записан ли уже студент
        existing_attendance = session.exec(
            select(Attendance).where(
                and_(
                    Attendance.student_id == student.id,
                    Attendance.class_id == class_id
                )
            )
        ).first()
        if existing_attendance:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Студент уже записан на это занятие"
            )

        # Создаем запись о посещаемости
        attendance = Attendance(
            student_id=student.id,
            class_id=class_id,
            teacher_id=class_.teacher_id,
            presence=AttendanceStatus.REGISTERED
        )
        session.add(attendance)

        # Увеличиваем количество записанных студентов
        class_.current_capacity += 1
        session.add(class_)

        session.commit()

        return {
            "message": "Студент успешно записан на занятие",
            "attendance_id": attendance.id,
            "current_capacity": class_.current_capacity,
            "hall_capacity": hall.capacity
        }

@app.get("/subscriptions/{student_id}", response_model=List[SubscriptionResponse])
async def get_student_subscription(
    student_id: int,
    current_user: Users = Depends(get_current_user)
):
    """Получение активных подписок студента"""
    try:
        print(f"Attempting to get subscriptions for student_id: {student_id}")
        print(f"Current user: {current_user.email}, role: {current_user.role}")
        
        # Проверяем, что пользователь авторизован
        if not current_user:
            print("User not authenticated")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "message": "Ошибка авторизации",
                    "errors": ["Требуется авторизация для просмотра подписок"]
                }
            )
        
        # Получаем подписки
        with Session(engine) as session:
            subscriptions = get_active_subscriptions(session, student_id)
            if not subscriptions:
                print(f"No active subscriptions found for student_id: {student_id}")
                return []
            
            print(f"Found {len(subscriptions)} active subscriptions")
            return subscriptions
            
    except HTTPException as e:
        print(f"HTTP Exception: {str(e)}")
        raise e
    except ValidationError as e:
        print(f"Validation Error: {str(e)}")
        error_messages = []
        for error in e.errors():
            field = error.get("loc", ["unknown"])[0]
            error_type = error.get("type", "")
            message = error.get("msg", "Неизвестная ошибка валидации")
            
            print(f"Validation error - Field: {field}, Type: {error_type}, Message: {message}")
            
            # Преобразуем технические сообщения в понятные пользователю
            if error_type == "value_error.missing":
                error_messages.append(f"Отсутствует обязательное поле '{field}'")
            elif error_type == "type_error.none.not_allowed":
                error_messages.append(f"Поле '{field}' не может быть пустым")
            elif error_type == "type_error.integer":
                error_messages.append(f"Поле '{field}' должно быть числом")
            elif error_type == "type_error.date":
                error_messages.append(f"Поле '{field}' должно быть датой в формате ГГГГ-ММ-ДД")
            elif error_type == "value_error.str.regex":
                error_messages.append(f"Поле '{field}' имеет неверный формат")
            else:
                error_messages.append(f"Ошибка в поле '{field}': {message}")
        
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": "Некорректные данные подписки",
                "errors": error_messages
            }
        )
    except Exception as e:
        print(f"Unexpected error in get_student_subscription: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Ошибка получения данных подписки",
                "errors": [
                    "Произошла ошибка при получении данных подписки",
                    "Пожалуйста, попробуйте позже или обратитесь в поддержку"
                ]
            }
        )

@app.get("/attendance/{student_id}", response_model=Optional[Attendance])
async def get_student_attendance(
    student_id: int
):
    """Получение активной подписки студента"""
    try:
        print(f"Attempting to get subscription for student_id: {student_id}")
       
        
       
        
               
        # Получаем подписку
        with Session(engine) as session:
            attendance = get_student_attendance(session, student_id)
            if attendance is None:
                print(f"No active subscription found for student_id: {student_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "message": "Подписка не найдена",
                        "errors": [
                            "У студента нет активной подписки",
                            "Возможно, подписка истекла или еще не была приобретена"
                        ]
                    }
                )
            print(f"Found subscription: {attendance}")
            return attendance
            
    except HTTPException as e:
        print(f"HTTP Exception: {str(e)}")
        raise e
    except ValidationError as e:
        print(f"Validation Error: {str(e)}")
        error_messages = []
        for error in e.errors():
            field = error.get("loc", ["unknown"])[0]
            error_type = error.get("type", "")
            message = error.get("msg", "Неизвестная ошибка валидации")
            
            print(f"Validation error - Field: {field}, Type: {error_type}, Message: {message}")
            
          
        
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": "Некорректные данные подписки",
                "errors": error_messages
            }
        )
    except Exception as e:
        print(f"Unexpected error in get_student_subscription: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Ошибка получения данных подписки",
                "errors": [
                    "Произошла ошибка при получении данных подписки",
                    "Пожалуйста, попробуйте позже или обратитесь в поддержку"
                ]
            }
        )

@app.put("/classes/{class_id}", response_model=ClassResponse)
def update_class(
    class_id: int,
    class_data: UpdateClassRequest,
    current_user: Users = Depends(get_current_user)
):
    """Обновление информации о занятии"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только администраторы могут обновлять занятия"
        )
    
    with Session(engine) as session:
        class_ = session.exec(select(Classes).where(Classes.id == class_id)).first()
        if not class_:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Занятие не найдено"
            )
        
        # Проверка доступности зала
        hall = session.exec(select(Halls).where(Halls.id == class_data.hall_id)).first()
        if not hall:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Зал не найден"
            )
        
        # Проверка занятости преподавателя
        teacher = session.exec(select(Teachers).where(Teachers.id == class_data.teacher_id)).first()
        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Преподаватель не найден"
            )
        
        # Обновление данных занятия
        class_.time = class_data.time
        class_.type = class_data.type
        class_.hall_id = class_data.hall_id
        class_.teacher_id = class_data.teacher_id
        class_.date = class_data.date
        
        session.add(class_)
        session.commit()
        session.refresh(class_)
        
        return class_

@app.delete("/classes/{class_id}")
def delete_class(
    class_id: int,
    current_user: Users = Depends(get_current_user)
):
    """Удаление занятия"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только администраторы могут удалять занятия"
        )
    
    with Session(engine) as session:
        class_ = session.exec(select(Classes).where(Classes.id == class_id)).first()
        if not class_:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Занятие не найдено"
            )
        
        # Удаляем все записи о посещаемости для этого занятия
        attendance_records = session.exec(
            select(Attendance).where(Attendance.class_id == class_id)
        ).all()
        for record in attendance_records:
            session.delete(record)
        
        session.delete(class_)
        session.commit()
        
        return {"message": "Занятие успешно удалено"}

@app.post("/admin/teachers/", response_model=TeacherResponse)
def create_teacher(
    teacher_data: CreateTeacherRequest,
    current_user: Users = Depends(get_current_user)
):
    """Создание нового преподавателя (только для администратора)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только администраторы могут создавать преподавателей"
        )
    
    with Session(engine) as session:
        # Проверяем, не существует ли уже пользователь с таким email
        existing_user = session.exec(select(Users).where(Users.email == teacher_data.email)).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким email уже существует"
            )
        
        # Создаем пользователя
        user = Users(
            email=teacher_data.email,
            password_hash=get_password_hash(teacher_data.password),
            role=UserRole.TEACHER
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        
        # Создаем преподавателя
        teacher = Teachers(
            full_name=teacher_data.full_name,
            phone=teacher_data.phone,
            experience=teacher_data.experience,
            specialization=teacher_data.specialization,
            user_id=user.id
        )
        session.add(teacher)
        session.commit()
        session.refresh(teacher)
        
        return TeacherResponse(
            id=teacher.id,
            full_name=teacher.full_name,
            email=user.email,
            phone=teacher.phone,
            experience=teacher.experience,
            specialization=teacher.specialization
        )

@app.put("/admin/teachers/{teacher_id}", response_model=TeacherResponse)
def update_teacher(
    teacher_id: int,
    teacher_data: UpdateTeacherRequest,
    current_user: Users = Depends(get_current_user)
):
    """Обновление информации о преподавателе (только для администратора)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только администраторы могут обновлять информацию о преподавателях"
        )
    
    with Session(engine) as session:
        teacher = session.exec(select(Teachers).where(Teachers.id == teacher_id)).first()
        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Преподаватель не найден"
            )
        
        user = session.exec(select(Users).where(Users.id == teacher.user_id)).first()
        
        # Обновляем данные преподавателя
        if teacher_data.full_name is not None:
            teacher.full_name = teacher_data.full_name
        if teacher_data.phone is not None:
            teacher.phone = teacher_data.phone
        if teacher_data.experience is not None:
            teacher.experience = teacher_data.experience
        if teacher_data.specialization is not None:
            teacher.specialization = teacher_data.specialization
        
        # Обновляем данные пользователя
        if teacher_data.email is not None:
            # Проверяем, не занят ли email другим пользователем
            existing_user = session.exec(
                select(Users)
                .where(Users.email == teacher_data.email)
                .where(Users.id != user.id)
            ).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email уже используется другим пользователем"
                )
            user.email = teacher_data.email
        
        if teacher_data.password is not None:
            user.password_hash = get_password_hash(teacher_data.password)
        
        session.add(teacher)
        session.add(user)
        session.commit()
        session.refresh(teacher)
        
        return TeacherResponse(
            id=teacher.id,
            full_name=teacher.full_name,
            email=user.email,
            phone=teacher.phone,
            experience=teacher.experience,
            specialization=teacher.specialization
        )

@app.delete("/admin/teachers/{teacher_id}")
def delete_teacher(
    teacher_id: int,
    current_user: Users = Depends(get_current_user)
):
    """Удаление преподавателя (только для администратора)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только администраторы могут удалять преподавателей"
        )
    
    with Session(engine) as session:
        teacher = session.exec(select(Teachers).where(Teachers.id == teacher_id)).first()
        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Преподаватель не найден"
            )
        
        # Проверяем, нет ли у преподавателя будущих занятий
        future_classes = session.exec(
            select(Classes)
            .where(Classes.teacher_id == teacher_id)
            .where(Classes.date >= date.today())
        ).all()
        
        if future_classes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Невозможно удалить преподавателя, у которого есть будущие занятия"
            )
        
        # Удаляем записи о посещаемости занятий преподавателя
        attendance_records = session.exec(
            select(Attendance)
            .join(Classes, Attendance.class_id == Classes.id)
            .where(Classes.teacher_id == teacher_id)
        ).all()
        
        for record in attendance_records:
            session.delete(record)
        
        # Удаляем занятия преподавателя
        classes = session.exec(
            select(Classes).where(Classes.teacher_id == teacher_id)
        ).all()
        
        for class_ in classes:
            session.delete(class_)
        
        # Удаляем пользователя и преподавателя
        user = session.exec(select(Users).where(Users.id == teacher.user_id)).first()
        session.delete(teacher)
        session.delete(user)
        session.commit()
        
        return {"message": "Преподаватель успешно удален"}

@app.post("/students/", response_model=StudentResponse)
def create_student(
    student_data: CreateStudentRequest,
    current_user: Users = Depends(get_current_user)
):
    """Создание нового студента"""
    try:
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Только администратор может создавать студентов"
            )
        
        with Session(engine) as session:
            # Проверяем, не существует ли уже пользователь с таким email
            existing_user = session.exec(select(Users).where(Users.email == student_data.email)).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Пользователь с таким email уже существует"
                )
            
            # Создаем пользователя
            user = Users(
                email=student_data.email,
                password_hash=get_password_hash(student_data.password),
                role=UserRole.STUDENT
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            
            # Создаем студента
            student = Students(
                user_id=user.id,
                full_name=student_data.full_name,
                phone=student_data.phone,
                date_of_birth=student_data.date_of_birth,
                gender=student_data.gender
            )
            session.add(student)
            session.commit()
            session.refresh(student)
            
            return StudentResponse(
                id=student.id,
                full_name=student.full_name,
                email=user.email,
                phone=student.phone,
                date_of_birth=student.date_of_birth,
                gender=student.gender
            )
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Ошибка при создании студента: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при создании студента: {str(e)}"
        )

@app.put("/students/{student_id}", response_model=StudentResponse)
def update_student(
    student_id: int,
    student_data: UpdateStudentRequest,
    current_user: Users = Depends(get_current_user)
):
    """Обновление информации о студенте"""
    try:
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Только администратор может обновлять информацию о студентах"
            )
        
        with Session(engine) as session:
            student = session.exec(select(Students).where(Students.id == student_id)).first()
            if not student:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Студент не найден"
                )
            
            user = session.exec(select(Users).where(Users.id == student.user_id)).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Пользователь не найден"
                )
            
            # Обновляем данные пользователя
            if student_data.email:
                # Проверяем, не занят ли email другим пользователем
                existing_user = session.exec(
                    select(Users).where(
                        and_(
                            Users.email == student_data.email,
                            Users.id != user.id
                        )
                    )
                ).first()
                if existing_user:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Пользователь с таким email уже существует"
                    )
                user.email = student_data.email
            
            if student_data.password:
                user.password_hash = get_password_hash(student_data.password)
            
            # Обновляем данные студента
            if student_data.full_name:
                student.full_name = student_data.full_name
            if student_data.phone:
                student.phone = student_data.phone
            if student_data.date_of_birth:
                student.date_of_birth = student_data.date_of_birth
            if student_data.gender:
                student.gender = student_data.gender
            
            session.add(user)
            session.add(student)
            session.commit()
            session.refresh(student)
            
            return StudentResponse(
                id=student.id,
                full_name=student.full_name,
                email=user.email,
                phone=student.phone,
                date_of_birth=student.date_of_birth,
                gender=student.gender
            )
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Ошибка при обновлении студента: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обновлении данных студента: {str(e)}"
        )

@app.delete("/students/{student_id}")
def delete_student(
    student_id: int,
    current_user: Users = Depends(get_current_user)
):
    """Удаление студента"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только администратор может удалять студентов"
        )
    
    with Session(engine) as session:
        student = session.exec(select(Students).where(Students.id == student_id)).first()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Студент не найден"
            )
        
        # Получаем связанного пользователя
        user = session.exec(select(Users).where(Users.id == student.user_id)).first()
        
        # Удаляем все связанные записи посещаемости
        attendance_records = session.exec(
            select(Attendance).where(Attendance.student_id == student_id)
        ).all()
        for record in attendance_records:
            session.delete(record)
        
        # Удаляем все связанные подписки
        subscriptions = session.exec(
            select(Subscriptions).where(Subscriptions.student_id == student_id)
        ).all()
        for subscription in subscriptions:
            session.delete(subscription)
        
        # Удаляем студента
        session.delete(student)
        
        # Удаляем пользователя
        if user:
            session.delete(user)
        
        session.commit()
        
        return {"message": "Студент успешно удален"}

@app.put("/attendance/{attendance_id}", response_model=AttendanceResponse)
async def update_attendance(
    attendance_id: int,
    attendance_data: UpdateAttendanceRequest,
    current_user: Users = Depends(get_current_user)
):
    """Обновление статуса посещаемости"""
    with Session(engine) as session:
        # Проверяем, что пользователь является администратором
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Только администраторы могут обновлять статус посещаемости"
            )

        # Получаем запись о посещаемости
        attendance = session.get(Attendance, attendance_id)
        if not attendance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Запись о посещаемости не найдена"
            )

        # Если статус меняется на "Присутствовал", списываем занятие
        if attendance_data.presence == "Присутствовал" and attendance.presence != "Присутствовал":
            # Получаем активную подписку студента
            subscription = session.exec(
                select(Subscriptions)
                .where(
                    and_(
                        Subscriptions.student_id == attendance.student_id,
                        Subscriptions.status == SubscriptionStatus.ACTIVE,
                        Subscriptions.remaining_classes > 0
                    )
                )
            ).first()

            if not subscription:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="У студента нет активной подписки или закончились занятия"
                )

            # Уменьшаем количество оставшихся занятий
            subscription.remaining_classes -= 1
            if subscription.remaining_classes == 0:
                subscription.status = SubscriptionStatus.EXPIRED

            session.add(subscription)

        # Обновляем статус
        attendance.presence = attendance_data.presence
        session.commit()

        # Получаем информацию о студенте и занятии
        student = session.get(Students, attendance.student_id)
        class_ = session.get(Classes, attendance.class_id)
        hall = session.get(Halls, class_.hall_id)
        teacher = session.get(Teachers, class_.teacher_id)
        return AttendanceResponse(
            id=attendance.id,
            presence=attendance.presence,
            student_id=attendance.student_id,
            class_id=attendance.class_id,
            teacher_id=attendance.teacher_id,
            student_name=student.full_name,
            class_=ClassResponse(
                id=class_.id,
                time=class_.time.strftime('%H:%M:%S'),
                type=class_.type,
                date=class_.date,
                current_capacity=class_.current_capacity,
                hall_number=hall.hall_number,
                hall_capacity=hall.capacity,
                teacher_name=teacher.full_name,
                specialization=teacher.specialization,
                remaining_slots=hall.capacity - class_.current_capacity,
                formatted_date=class_.date.strftime('%d.%m.%Y'),
                formatted_time=class_.time.strftime('%H:%M'),
                day_of_week=class_.date.strftime('%A'),
                teacher_id=class_.teacher_id,
                hall_id=class_.hall_id
            )
        )

@app.post("/payments/create-with-subscription", response_model=PaymentAndSubscriptionResponse)
async def create_payment_and_subscription(
    request: CreatePaymentAndSubscriptionRequest,
    current_user: Users = Depends(get_current_user)
):
    """
    Создание платежа и подписки в рамках одной транзакции.
    Только студенты могут создавать платежи и подписки для себя.
    """
    try:
        print(f"Начало создания платежа и подписки для студента {request.student_id}")
        
        # Проверяем, что текущий пользователь - студент
        if current_user.role != UserRole.STUDENT:
            print(f"Ошибка: пользователь {current_user.email} не является студентом")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "message": "Доступ запрещен",
                    "errors": ["Только студенты могут создавать платежи и подписки"]
                }
            )

        # Получаем информацию о студенте
        with Session(engine) as session:
            print(f"Поиск студента с ID {request.student_id}")
            student = session.get(Students, request.student_id)
            if not student:
                print(f"Студент с ID {request.student_id} не найден")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "message": "Студент не найден",
                        "errors": ["Указанный студент не существует в системе"]
                    }
                )

            # Проверяем, что студент создает платеж для себя
            if student.user_id != current_user.id:
                print(f"Ошибка: студент {student.id} пытается создать платеж для другого студента")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "message": "Доступ запрещен",
                        "errors": ["Вы можете создавать платежи и подписки только для себя"]
                    }
                )

            try:
                # Начинаем транзакцию
                print("Начало транзакции...")
                
                # Создаем платеж
                print("Создание платежа...")
                payment = Payments(
                    student_id=request.student_id,
                    amount=request.amount,
                    payment_method=request.payment_method,
                    status=PaymentStatus.COMPLETED,
                    payment_date=datetime.now()
                )
                print(f"Платеж создан: {payment}")
                session.add(payment)
                session.flush()  # Получаем ID платежа без коммита транзакции
                print(f"Платеж сохранен с ID: {payment.id}")

                # Создаем подписку
                print("Создание подписки...")
                subscription = Subscriptions(
                    student_id=request.student_id,
                    payment_id=payment.id,
                    status=SubscriptionStatus.ACTIVE,
                    start_date=request.start_date,
                    end_date=request.start_date + relativedelta(months=1),
                    number_of_classes=request.number_of_classes,
                    remaining_classes=request.number_of_classes,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                print(f"Подписка создана с number_of_classes={request.number_of_classes}")
                session.add(subscription)
                session.flush()  # Получаем ID подписки без коммита транзакции
                session.refresh(subscription)  # Обновляем объект, чтобы получить все поля
                print(f"Подписка сохранена с ID: {subscription.id}, number_of_classes: {subscription.number_of_classes}")

                # Подтверждаем транзакцию
                session.commit()
                print("Транзакция успешно завершена")

                # Обновляем объекты после коммита
                session.refresh(payment)
                session.refresh(subscription)

                return PaymentAndSubscriptionResponse(
                    payment=Payments(
                        id=payment.id,
                        student_id=payment.student_id,
                        amount=payment.amount,
                        payment_date=payment.payment_date,
                        payment_method=payment.payment_method,
                        status=payment.status
                    ),
                    subscription=Subscriptions(
                        id=subscription.id,
                        start_date=subscription.start_date,
                        end_date=subscription.end_date,
                        number_of_classes=subscription.number_of_classes,
                        remaining_classes=subscription.remaining_classes,
                        status=subscription.status,
                        student_id=subscription.student_id,
                        payment_id=subscription.payment_id,
                        created_at=subscription.created_at,
                        updated_at=subscription.updated_at
                    )
                )

            except Exception as e:
                print(f"Ошибка при создании платежа и подписки: {str(e)}")
                session.rollback()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={
                        "message": "Ошибка при создании платежа и подписки",
                        "errors": [f"Произошла ошибка: {str(e)}"]
                    }
                )

    except ValidationError as e:
        print(f"Ошибка валидации: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": "Ошибка валидации данных",
                "errors": [{"field": err["loc"][0], "message": err["msg"]} for err in e.errors()]
            }
        )
    except HTTPException as e:
        print(f"HTTP ошибка: {str(e)}")
        raise e
    except Exception as e:
        print(f"Непредвиденная ошибка: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Внутренняя ошибка сервера",
                "errors": [f"Произошла непредвиденная ошибка: {str(e)}"]
            }
        )

@app.get("/teachers/{teacher_id}/schedule", response_model=List[ClassResponse])
async def get_teacher_schedule_endpoint(
    teacher_id: int,
    current_user: Users = Depends(get_current_user)
):
    """Получение расписания конкретного преподавателя"""
    try:
        with Session(engine) as session:
            # Проверяем, что пользователь имеет доступ к этому расписанию
            if current_user.role != UserRole.ADMIN:
                # Для преподавателей проверяем, что это их собственное расписание
                teacher = session.exec(
                    select(Teachers)
                    .where(Teachers.user_id == current_user.id)
                ).first()
                if not teacher or teacher.id != teacher_id:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Нет доступа к этому расписанию"
                    )

            # Получаем все занятия преподавателя
            classes = session.exec(
                select(Classes)
                .where(Classes.teacher_id == teacher_id)
                .order_by(Classes.date, Classes.time)
            ).all()

            # Формируем ответ
            schedule = []
            for class_item in classes:
                hall = session.get(Halls, class_item.hall_id)
                teacher = session.get(Teachers, class_item.teacher_id)
                
                schedule.append({
                    "id": class_item.id,
                    "type": class_item.type,
                    "time": class_item.time.strftime("%H:%M"),
                    "date": class_item.date,
                    "hall_number": hall.hall_number if hall else None,
                    "hall_capacity": hall.capacity if hall else 0,
                    "current_capacity": class_item.current_capacity,
                    "teacher_name": teacher.full_name if teacher else None,
                    "formatted_date": class_item.date.strftime("%d.%m.%Y"),
                    "formatted_time": class_item.time.strftime("%H:%M"),
                    "teacher_id": class_item.teacher_id,
                    "hall_id": class_item.hall_id
                })

            return schedule
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении расписания: {str(e)}"
        )