-- Удаление существующих таблиц (если нужно пересоздать базу)
DROP TABLE IF EXISTS admins, users, students, teachers, payments, subscriptions, halls, classes, attendance;
DROP SCHEMA IF EXISTS public CASCADE;
CREATE SCHEMA public;

-- Создание enum для ролей
CREATE TYPE user_role AS ENUM ('student', 'teacher', 'admin');

-- Создание таблицы пользователей
CREATE TABLE "users" (
  "id" serial PRIMARY KEY,
  "email" varchar(50) NOT NULL UNIQUE,
  "password_hash" varchar(100) NOT NULL,
  "role" user_role NOT NULL,
  "created_at" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updated_at" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Создание таблиц БЕЗ внешних ключей
CREATE TABLE "students" (
  "id" serial PRIMARY KEY,
  "user_id" int NOT NULL,
  "full_name" varchar(50) NOT NULL,
  "date_of_birth" date NOT NULL,
  "gender" varchar(1) NOT NULL CHECK (gender IN ('M', 'F')),
  "phone" varchar(12) NOT NULL CHECK (phone ~ '^\+7\d{10}$'),
  "created_at" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updated_at" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "payments" (
  "id" serial PRIMARY KEY,
  "student_id" int NOT NULL,
  "amount" float NOT NULL CHECK (amount > 0),
  "payment_date" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "payment_method" varchar(20) NOT NULL DEFAULT 'card' CHECK (payment_method IN ('card', 'cash', 'bank_transfer')),
  "status" varchar(20) NOT NULL DEFAULT 'completed' CHECK (status IN ('completed', 'pending', 'failed'))
);

CREATE TABLE "teachers" (
  "id" serial PRIMARY KEY,
  "user_id" int NOT NULL,
  "full_name" varchar(50) NOT NULL,
  "experience" int NOT NULL CHECK (experience >= 0 AND experience <= 50),
  "specialization" varchar(20) NOT NULL,
  "phone" varchar(12) NOT NULL CHECK (phone ~ '^\+7\d{10}$'),
  "created_at" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updated_at" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "subscriptions" (
  "id" serial PRIMARY KEY,
  "start_date" date NOT NULL DEFAULT CURRENT_DATE,
  "end_date" date NOT NULL DEFAULT (CURRENT_DATE + INTERVAL '1 month'),
  "number_of_classes" int NOT NULL CHECK (number_of_classes >= 0 AND number_of_classes <= 16),
  "remaining_classes" int NOT NULL CHECK (remaining_classes >= 0 AND remaining_classes <= 16),
  "status" varchar(10) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'expired')),
  "student_id" int NOT NULL,
  "payment_id" int NOT NULL,
  "created_at" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updated_at" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CHECK (end_date >= start_date)
);

CREATE TABLE "halls" (
  "id" serial PRIMARY KEY,
  "hall_number" int NOT NULL UNIQUE,
  "capacity" int NOT NULL CHECK (capacity > 0 AND capacity <= 100),
  "description" varchar(200) DEFAULT '',
  "created_at" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updated_at" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "classes" (
  "id" serial PRIMARY KEY,
  "time" time NOT NULL,
  "type" varchar(18) NOT NULL,
  "hall_id" int,
  "teacher_id" int NOT NULL,
  "date" DATE NOT NULL,
  "current_capacity" int NOT NULL DEFAULT 0 CHECK (current_capacity >= 0),
  "created_at" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updated_at" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "attendance" (
  "id" serial PRIMARY KEY,
  "presence" varchar(15) NOT NULL DEFAULT 'Записан' CHECK (presence IN ('Записан', 'Присутствовал')),
  "student_id" int,
  "class_id" int,
  "teacher_id" int,
  "created_at" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updated_at" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "admins" (
  "id" serial PRIMARY KEY,
  "user_id" int NOT NULL,
  "full_name" varchar(50) NOT NULL,
  "created_at" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updated_at" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Добавление внешних ключей через ALTER TABLE
ALTER TABLE "students" ADD CONSTRAINT fk_students_user_id 
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE "teachers" ADD CONSTRAINT fk_teachers_user_id 
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE "payments" ADD CONSTRAINT fk_payments_student_id 
  FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE;

ALTER TABLE "subscriptions" ADD CONSTRAINT fk_subscriptions_student_id 
  FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE;

ALTER TABLE "subscriptions" ADD CONSTRAINT fk_subscriptions_payment_id 
  FOREIGN KEY (payment_id) REFERENCES payments(id) ON DELETE CASCADE;

ALTER TABLE "classes" ADD CONSTRAINT fk_classes_hall_id 
  FOREIGN KEY (hall_id) REFERENCES halls(id) ON DELETE SET NULL;

ALTER TABLE "classes" ADD CONSTRAINT fk_classes_teacher_id 
  FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE;

ALTER TABLE "attendance" ADD CONSTRAINT fk_attendance_student_id 
  FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE SET NULL;

ALTER TABLE "attendance" ADD CONSTRAINT fk_attendance_class_id 
  FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE SET NULL;

ALTER TABLE "attendance" ADD CONSTRAINT fk_attendance_teacher_id 
  FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE SET NULL;

ALTER TABLE "admins" ADD CONSTRAINT fk_admins_user_id 
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- Создание индексов
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_students_user_id ON students(user_id);
CREATE INDEX idx_payments_students_id ON payments(student_id);
CREATE INDEX idx_teachers_user_id ON teachers(user_id);
CREATE INDEX idx_classes_date ON classes(date);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);
CREATE INDEX idx_attendance_student_id ON attendance(student_id);
CREATE INDEX idx_attendance_class_id ON attendance(class_id);
CREATE INDEX idx_admins_user_id ON admins(user_id);

-- Триггеры для обновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_students_updated_at
    BEFORE UPDATE ON students
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_teachers_updated_at
    BEFORE UPDATE ON teachers
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_subscriptions_updated_at
    BEFORE UPDATE ON subscriptions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_halls_updated_at
    BEFORE UPDATE ON halls
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_classes_updated_at
    BEFORE UPDATE ON classes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_attendance_updated_at
    BEFORE UPDATE ON attendance
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_admins_updated_at
    BEFORE UPDATE ON admins
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE OR REPLACE FUNCTION check_remaining_classes()
RETURNS TRIGGER AS $$
BEGIN
-- Проверяем, изменилось ли remaining_classes и стало ли оно 0
IF NEW.remaining_classes = 0 AND (OLD.remaining_classes IS NULL OR OLD.remaining_classes <> 0) THEN
  NEW.status := 'expired';
END IF;
    
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 2. Создаём триггер, который срабатывает перед обновлением записи
CREATE TRIGGER update_status_when_no_classes_left
BEFORE UPDATE ON subscriptions
