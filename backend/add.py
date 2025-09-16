# Импорт необходимых модулей
from ll1 import SQLModel
from ll1 import *
from datetime import  date, time, timedelta
from passlib.context import CryptContext
from sqlmodel import Session, select
from main import get_password_hash

# Инициализация контекста для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def add_initial_data():
    """Добавление тестовых данных в базу данных"""
    SQLModel.metadata.create_all(engine)
      
    try:
        with Session(engine) as session:
            # Проверяем, есть ли уже данные в таблицах
            if session.exec(select(Users)).first():
                print("Данные уже существуют в базе")
                return

            print("Creating users...")
            
            # Создание пользователей (обезличенные учебные данные)
            admin_user = Users(
                email="admin@example.local",
                password_hash=get_password_hash("CHANGE_ME_ADMIN"),
                role=UserRole.ADMIN
            )

            student_user_1 = Users(
                email="student1@example.local",
                password_hash=get_password_hash("CHANGE_ME_STUDENT1"),
                role=UserRole.STUDENT
            )

            student_user_2 = Users(
                email="student2@example.local",
                password_hash=get_password_hash("CHANGE_ME_STUDENT2"),
                role=UserRole.STUDENT
            )

            teacher_user_1 = Users(
                email="teacher1@example.local",
                password_hash=get_password_hash("CHANGE_ME_TEACHER1"),
                role=UserRole.TEACHER
            )

            teacher_user_2 = Users(
                email="teacher2@example.local",
                password_hash=get_password_hash("CHANGE_ME_TEACHER2"),
                role=UserRole.TEACHER
            )

            print("Adding users to database...")
            session.add(admin_user)
            session.add(student_user_1)
            session.add(student_user_2)
            session.add(teacher_user_1)
            session.add(teacher_user_2)
            session.commit()
            session.refresh(admin_user)
            session.refresh(student_user_1)
            session.refresh(student_user_2)
            session.refresh(teacher_user_1)
            session.refresh(teacher_user_2)
            print("Users created successfully")

            print("Creating admin...")
            admin = Admins(
                user_id=admin_user.id,  # Убедитесь, что передаёте user_id
                full_name="Администратор"
            )
            session.add(admin)
            session.commit()
            session.refresh(admin)
            print("Admin created successfully")

            print("Creating students...")
            student_1 = Students(
                user_id=student_user_1.id,
                full_name="Студент Один",
                date_of_birth=date(1995, 5, 15),
                gender=Gender.MALE,
                phone="+70000000001"
            )

            student_2 = Students(
                user_id=student_user_2.id,
                full_name="Студент Два",
                date_of_birth=date(1998, 8, 20),
                gender=Gender.FEMALE,
                phone="+70000000002"
            )

            print("Adding students to database...")
            session.add(student_1)
            session.add(student_2)
            session.commit()
            session.refresh(student_1)
            session.refresh(student_2)
            print("Students created successfully")

            print("Creating teachers...")
            teacher_1 = Teachers(
                user_id=teacher_user_1.id,
                full_name="Преподаватель Один",
                experience=5,
                specialization="Jazz-funk",
                phone="+70000000003"
            )

            teacher_2 = Teachers(
                user_id=teacher_user_2.id,
                full_name="Преподаватель Два",
                experience=3,
                specialization="Hip-hop",
                phone="+70000000004"
            )

            print("Adding teachers to database...")
            session.add(teacher_1)
            session.add(teacher_2)
            session.commit()
            session.refresh(teacher_1)
            session.refresh(teacher_2)
            print("Teachers created successfully")

            # Добавление платежей
            payment_1 = Payments(
                student_id=student_1.id,
                amount=3000.0,
                payment_method="card",
                status="completed"
            )

            payment_2 = Payments(
                student_id=student_2.id,
                amount=3000.0,
                payment_method="cash",
                status="completed"
            )

            payment_3 = Payments(
                student_id=student_2.id,
                amount=3000.0,
                payment_method="cash",
                status="completed"
            )

            print("Creating payments...")
            session.add(payment_1)
            session.add(payment_2)
            session.add(payment_3)
            session.commit()
            session.refresh(payment_1)
            session.refresh(payment_2)
            session.refresh(payment_3)
            print("Payments created successfully")

            # Добавление залов
            hall_1 = Halls(
                hall_number=101,
                capacity=20,
                description="Большой зал с зеркалами"
            )

            hall_2 = Halls(
                hall_number=102,
                capacity=15,
                description="Малый зал с паркетом"
            )

            print("Creating halls...")
            session.add(hall_1)
            session.add(hall_2)
            session.commit()
            session.refresh(hall_1)
            session.refresh(hall_2)
            print("Halls created successfully")

            # Добавление абонементов
            subscription_1 = Subscriptions(
                student_id=student_1.id,
                payment_id=payment_1.id,
                status=SubscriptionStatus.ACTIVE,
                number_of_classes=8,
                remaining_classes=8,
                start_date=date.today(),
                end_date=date.today() + timedelta(days=30)
            )

            subscription_2 = Subscriptions(
                student_id=student_2.id,
                payment_id=payment_2.id,
                status=SubscriptionStatus.EXPIRED,
                number_of_classes=8,
                remaining_classes=6,
                start_date=date.today()-timedelta(days=30),
                end_date=date.today()-  timedelta(days=25)
            )

            subscription_3 = Subscriptions(
                student_id=student_2.id,
                payment_id=payment_3.id,
                status=SubscriptionStatus.ACTIVE,
                number_of_classes=8,
                remaining_classes=8,
                start_date=date.today(),
                end_date=date.today() + timedelta(days=30)
            )

            print("Creating subscriptions...")
            session.add(subscription_1)
            session.add(subscription_2)
            session.add(subscription_3)
            session.commit()
            session.refresh(subscription_1)
            session.refresh(subscription_2)
            session.refresh(subscription_3)
            print("Subscriptions created successfully")

            # Добавление занятий
            class_1 = Classes(
                time=time(19, 0),
                type="Jazz-funk",
                hall_id=hall_1.id,
                teacher_id=teacher_1.id,
                date=date.today() + timedelta(days=1),  # Занятие на завтра
                current_capacity=0
            )

            class_2 = Classes(
                time=time(20, 0),
                type="Hip-hop",
                hall_id=hall_2.id,
                teacher_id=teacher_2.id,
                date=date.today()+ timedelta(days=2),  # Занятие послезавтра
                current_capacity=0
            )
            class_3 = Classes(
                time=time(21, 0),
                type="Hip-hop",
                hall_id=hall_2.id,
                teacher_id=teacher_2.id,
                date=date.today() + timedelta(days=3),  # Занятие через 3 дня
                current_capacity=0
            )

            print("Creating classes...")
            session.add(class_1)
            session.add(class_2)
            session.add(class_3)
            session.commit()
            session.refresh(class_1)
            session.refresh(class_2)
            session.refresh(class_3)
            print("Classes created successfully")

            # Добавление посещаемости
            attendance_1 = Attendance(
                presence="Присутствовал",
                student_id=student_1.id,
                class_id=class_1.id,
                teacher_id=teacher_1.id
            )

            attendance_2 = Attendance(
                presence="Присутствовал",
                student_id=student_2.id,
                class_id=class_2.id,
                teacher_id=teacher_2.id
            )

            print("Creating attendance records...")
            session.add(attendance_1)
            session.add(attendance_2)
            session.commit()
            print("Attendance records created successfully")

            print("Все данные успешно добавлены!")

    except Exception as e:
        print(f"Ошибка при добавлении данных: {e}")
        raise

def add_test_class():
    with Session(engine) as session:
        # Используем существующий зал
        hall = session.exec(select(Halls).where(Halls.hall_number == 101)).first()
        if not hall:
            print("Зал не найден, создаем новый")
            hall = Halls(hall_number=101, capacity=20, description="Основной зал")
            session.add(hall)
            session.commit()
            session.refresh(hall)

        # Проверяем наличие преподавателя
        teacher = session.exec(select(Teachers).where(Teachers.full_name == "Иванов Иван")).first()
        if not teacher:
            # Создаем пользователя для преподавателя
            user = Users(
                email="teacher_temp@example.local",
                password_hash=get_password_hash("CHANGE_ME_TEACHER_TMP"),
                role=UserRole.TEACHER
            )
            session.add(user)
            session.commit()
            session.refresh(user)

            teacher = Teachers(
                user_id=user.id,
                full_name="Иванов Иван",
                experience=5,
                specialization="Бальные танцы",
                phone="+79999999999"
            )
            session.add(teacher)
            session.commit()
            session.refresh(teacher)

        # Создаем тестовое занятие
        test_class = Classes(
            time=time(10, 0),  # 10:00
            type="Бальные танцы",
            hall_id=hall.id,
            teacher_id=teacher.id,
            date=date(2025, 3, 29),  # 29 марта 2025
            current_capacity=0
        )
        try:
            session.add(test_class)
            session.commit()
            print("Тестовое занятие успешно добавлено")
        except Exception as e:
            print(f"Ошибка при добавлении занятия: {str(e)}")
            session.rollback()
            raise

if __name__ == "__main__":
    # Запуск функции добавления данных
    add_initial_data()
    add_test_class()    
