# Импорт необходимых модулей
from ll1 import *
from sqlalchemy import func, and_, or_, exists
from datetime import  date, timedelta
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
from dateutil.relativedelta import relativedelta

def get_classes_with_details(
    start_date: date = date.today(),
    end_date: date = date.today() + timedelta(days=7),
    dance_type: Optional[str] = None,
    teacher_id: Optional[int] = None
) -> List[dict]:
    """Получение расписания с деталями о зале и преподавателе"""
    with Session(engine) as session:
        query = (
            select(
                Classes,
                Halls.hall_number,
                Halls.capacity,
                Teachers.full_name,
                Teachers.specialization
            )
            .join(Halls, Classes.hall_id == Halls.id)
            .join(Teachers, Classes.teacher_id == Teachers.id)
            .where(
                Classes.date >= start_date,
                Classes.date <= end_date
            )
        )
        
        if dance_type:
            query = query.where(Classes.type == dance_type)
        if teacher_id:
            query = query.where(Classes.teacher_id == teacher_id)
            
        results = session.exec(query).all()
        
        return [
            {
                "id": cls.id,
                "time": cls.time,
                "type": cls.type,
                "date": cls.date,
                "current_capacity": cls.current_capacity,
                "hall_number": hall_number,
                "hall_capacity": capacity,
                "teacher_name": teacher_name,
                "specialization": specialization,
                "remaining_slots": capacity - cls.current_capacity
            }
            for cls, hall_number, capacity, teacher_name, specialization in results
        ]

def get_students_with_email() -> List[dict]:
    """Получение студентов с их email"""
    with Session(engine) as session:
        query = (
            select(
                Students,
                Users.email
            )
            .join(Users, Students.user_id == Users.id)
        )
        results = session.exec(query).all()
        
        return [
            {
                "id": student.id,
                "full_name": student.full_name,
                "email": email,
                "phone": student.phone,
                "date_of_birth": student.date_of_birth,
                "gender": student.gender
            }
            for student, email in results
        ]
    
def get_student_by_email(email: str) -> Optional[Students]:
    """Получение студента по email"""
    try:
        with Session(engine) as session:
            print(f"Searching for student with email: {email}")  # Отладочный вывод
            statement = select(Students).where(Students.email == email)
            student = session.exec(statement).first()
            if student:
                print(f"Found student: {student.email}")  # Отладочный вывод
            else:
                print("Student not found")  # Отладочный вывод
            return student
    except Exception as e:
        print(f"Error in get_student_by_email: {e}")  # Отладочный вывод
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

def get_active_subscription(db: Session, student_id: int) -> Optional[Subscriptions]:
    """Получение активной подписки студента"""
    with Session(engine) as session:
        try:
            # Проверяем существование студента
            student = db.exec(
                select(Students).where(Students.id == student_id)
            ).first()
            
            if not student:
                print(f"Student with id {student_id} not found")
                return None

            # Получаем активную подписку
            subscription = db.exec(
                select(Subscriptions).where(
                    and_(
                        Subscriptions.student_id == student_id,
                        Subscriptions.end_date >= date.today()
                    )
                )
            ).first()

            if not subscription:
                print(f"No active subscription found for student {student_id}")
                return None

            return subscription

        except Exception as e:
            print(f"Error getting subscription: {str(e)}")
            return None

def get_active_subscriptions(db: Session, student_id: int) -> List[Subscriptions]:
    """
    Получение всех активных подписок студента.
    Активной считается подписка, у которой:
    1. end_date >= текущей даты
    2. status = 'active'
    3. remaining_classes > 0
    """
    try:
        # Получаем текущую дату
        current_date = date.today()
        print(f"Current date: {current_date}")
        
        # Получаем все подписки студента для отладки
        all_subscriptions = db.exec(
            select(Subscriptions).where(
                Subscriptions.student_id == student_id
            )
        ).all()
        
        print(f"All subscriptions for student {student_id}:")
        for sub in all_subscriptions:
            print(f"Subscription {sub.id}: start_date={sub.start_date}, end_date={sub.end_date}, status={sub.status}, remaining_classes={sub.remaining_classes}")

        # Получаем активные подписки
        subscriptions = db.exec(
            select(Subscriptions).where(
                and_(
                    Subscriptions.student_id == student_id,
                    Subscriptions.end_date >= current_date,
                    Subscriptions.status == SubscriptionStatus.ACTIVE,
                    Subscriptions.remaining_classes > 0
                )
            )
        ).all()

        print(f"Found {len(subscriptions)} active subscriptions")
        return subscriptions

    except Exception as e:
        print(f"Ошибка при получении активных подписок: {str(e)}")
        return []

def get_class_schedule(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    dance_type: Optional[str] = None,
    teacher_id: Optional[int] = None
) -> List[Classes]:
    """Получение расписания занятий с фильтрацией"""
    with Session(engine) as session:
        statement = select(Classes)
        if date_from:
            if date_from < date.today():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Start date cannot be in the past"
                )
            statement = statement.where(Classes.date >= date_from)
        if date_to:
            if date_to < date_from if date_from else date.today():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="End date cannot be before start date"
                )
            statement = statement.where(Classes.date <= date_to)
        if dance_type:
            statement = statement.where(Classes.type == dance_type)
        if teacher_id:
            statement = statement.where(Classes.teacher_id == teacher_id)
        return session.exec(statement).all()

def get_available_classes(student_id: int) -> List[Classes]:
    """Получение доступных для записи занятий"""
    with Session(engine) as session:
        subscription = get_active_subscription(session, student_id)
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active subscription found"
            )

        statement = select(Classes).where(
            and_(
                Classes.date >= date.today(),
                ~exists().where(
                    and_(
                        Attendance.class_id == Classes.id,
                        Attendance.student_id == student_id
                    )
                )
            )
        )
        return session.exec(statement).all()

def enroll_student_in_class(student_id: int, class_id: int) -> Dict[str, Any]:
    with Session(engine) as session:
        try:
            # Проверяем наличие активного абонемента
            subscription = get_active_subscription(session, student_id)
            if not subscription:
                raise HTTPException(
                    status_code=400,
                    detail="No active subscription found"
                )

            # Получаем информацию о занятии
            class_ = session.get(Classes, class_id)
            if not class_:
                raise HTTPException(
                    status_code=404,
                    detail="Class not found"
                )

            # Получаем информацию о зале
            hall = session.get(Halls, class_.hall_id)
            if not hall:
                raise HTTPException(
                    status_code=404,
                    detail="Hall not found"
                )

            # Проверяем вместимость зала
            if class_.current_capacity >= hall.capacity:
                raise HTTPException(
                    status_code=400,
                    detail="Class is full"
                )

            # Проверяем, не записан ли уже студент на это занятие
            existing_enrollment = session.exec(
                select(Attendance).where(
                    Attendance.student_id == student_id,
                    Attendance.class_id == class_id
                )
            ).first()

            if existing_enrollment:
                raise HTTPException(
                    status_code=400,
                    detail="Student is already enrolled in this class"
                )

            # Создаем запись о посещении
            attendance = Attendance(
                student_id=student_id,
                class_id=class_id,
                presence="Записан",
                teacher_id=class_.teacher_id
            )
            session.add(attendance)
            print("11111111111111111111")

            # Увеличиваем текущую заполненность класса
            class_.current_capacity += 1

            # Сохраняем изменения
            session.commit()
            session.refresh(attendance)

            return {
                "message": "Successfully enrolled in class",
                "attendance_id": attendance.id,
                "remaining_slots": hall.capacity - class_.current_capacity
            }

        except HTTPException as e:
            raise e
        except Exception as e:
            session.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error enrolling in class: {str(e)}"
            )

def mark_attendance(student_id: int, class_id: int, presence: str) -> Dict[str, Any]:
    """Отметка посещаемости"""
    with Session(engine) as session:
        attendance = session.exec(
            select(Attendance).where(
                and_(
                    Attendance.student_id == student_id,
                    Attendance.class_id == class_id
                )
            )
        ).first()

        if not attendance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attendance record not found"
            )

        attendance.presence = presence
        session.commit()
        return {"message": "Attendance marked successfully"}

def get_teacher_schedule(teacher_id: int, date_from: Optional[date] = None) -> List[Classes]:
    """Получение расписания преподавателя"""
    with Session(engine) as session:
        if date_from and date_from < date.today():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Start date cannot be in the past"
            )

        statement = select(Classes).where(Classes.teacher_id == teacher_id)
        if date_from:
            statement = statement.where(Classes.date >= date_from)
        return session.exec(statement).all()

def get_attendance_statistics(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    dance_type: Optional[str] = None,
    teacher_id: Optional[int] = None
) -> Dict[str, Any]:
    """Получение статистики посещаемости"""
    with Session(engine) as session:
        if date_from and date_to and date_to < date_from:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="End date cannot be before start date"
            )

        statement = select(Attendance).join(Classes)
        if date_from:
            statement = statement.where(Classes.date >= date_from)
        if date_to:
            statement = statement.where(Classes.date <= date_to)
        if dance_type:
            statement = statement.where(Classes.type == dance_type)
        if teacher_id:
            statement = statement.where(Classes.teacher_id == teacher_id)

        attendance_records = session.exec(statement).all()

        statistics = {
            "total_attendance": len(attendance_records),
            "by_dance_type": {},
            "by_teacher": {},
            "by_date": {},
            "attendance_rate": 0.0
        }

        total_registered = 0
        total_present = 0

        for record in attendance_records:
            dance_type = record.class_.type
            teacher_id = record.class_.teacher_id
            date_str = record.class_.date.strftime("%Y-%m-%d")

            statistics["by_dance_type"][dance_type] = statistics["by_dance_type"].get(dance_type, 0) + 1
            statistics["by_teacher"][teacher_id] = statistics["by_teacher"].get(teacher_id, 0) + 1
            statistics["by_date"][date_str] = statistics["by_date"].get(date_str, 0) + 1

            if record.presence == "Записан":
                total_registered += 1
            if record.presence == "Присутствовал":
                total_present += 1

        if total_registered > 0:
            statistics["attendance_rate"] = (total_present / total_registered) * 100

        return statistics

def get_student_attendance(student_id: int) -> List[Attendance]:
    """Получение посещаемости студента"""
    with Session(engine) as session:
        statement = select(Attendance).where(
            Attendance.student_id == student_id
        ).order_by(Attendance.created_at.desc())
        return session.exec(statement).all()

def get_class_attendance(class_id: int) -> List[Attendance]:
    """Получение посещаемости занятия"""
    with Session(engine) as session:
        statement = select(Attendance).where(
            Attendance.class_id == class_id
        ).order_by(Attendance.created_at.desc())
        return session.exec(statement).all()

def create_payment(student_id: int, amount: float, payment_method: str, status_payment:str) -> Payments:
    """Создание платежа"""
    with Session(engine) as session:
        payment = Payments(
            student_id=student_id,
            amount=amount,
            payment_method=payment_method,
            status=status_payment
        )
        session.add(payment)
        session.commit()
        session.refresh(payment)
        return payment

def create_subscription(student_id: int, payment_id: int, number_of_classes: int, start_date: date) -> Subscriptions:
    """Создание подписки"""
    with Session(engine) as session:
        # Проверяем существование платежа
        payment = session.get(Payments, payment_id)
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Платеж не найден"
            )

        # Проверяем, что платеж принадлежит студенту
        if payment.student_id != student_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Платеж не принадлежит указанному студенту"
            )

        # Создаем подписку
        subscription = Subscriptions(
            student_id=student_id,
            payment_id=payment_id,
            status=SubscriptionStatus.ACTIVE,
            start_date=start_date,
            end_date=start_date + relativedelta(months=1),
            number_of_classes=number_of_classes,
            remaining_classes=number_of_classes
        )
        session.add(subscription)
        session.commit()
        session.refresh(subscription)
        return subscription

def get_all_teachers() -> List[Teachers]:
    """Получение списка всех преподавателей"""
    with Session(engine) as session:
        statement = select(Teachers)
        return session.exec(statement).all()
    
def get_all_halls() -> List[Halls]:
    """Получение списка всех залов"""
    with Session(engine) as session:
        statement = select(Halls)
        return session.exec(statement).all()
    
def create_class(class_data: Dict[str, Any]) -> Classes:
    """Создание занятия"""
    with Session(engine) as session:
        # Проверка существования зала и преподавателя
        hall = session.get(Halls, class_data.get('hall_id'))
        if not hall:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hall not found"
            )

        teacher = session.get(Teachers, class_data.get('teacher_id'))
        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Teacher not found"
            )

        # Проверка на конфликты расписания
        existing_class = session.exec(
            select(Classes).where(
                and_(
                    Classes.hall_id == class_data['hall_id'],
                    Classes.date == class_data['date']
                )
            )
        ).first()
        if existing_class:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Hall is already booked for this time"
            )

        class_ = Classes(**class_data)
        session.add(class_)
        session.commit()
        session.refresh(class_)
        return class_

if __name__ == "__main__":
    # Тестовые вызовы функций
        enroll_student_in_class(1, 2)
    #mark_attendance(1,2,"Present")