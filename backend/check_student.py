from backend.ll1 import *
from sqlmodel import Session, select

def check_student_id():
    with Session(engine) as session:
        user = session.exec(
            select(Users).where(Users.email == 'ivan@example.com')
        ).first()
        
        if not user:
            print("Пользователь не найден")
            return
            
        student = session.exec(
            select(Students).where(Students.user_id == user.id)
        ).first()
        
        print(f"User ID: {user.id}")
        print(f"Student ID: {student.id if student else None}")
        print(f"Role: {user.role}")

if __name__ == "__main__":
    check_student_id() 