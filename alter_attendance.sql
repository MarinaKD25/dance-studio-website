-- Изменение таблицы attendance для установки значения по умолчанию для поля presence
ALTER TABLE attendance 
ALTER COLUMN presence SET DEFAULT 'Записан';

-- Проверка изменений
SELECT column_name, column_default 
FROM information_schema.columns 
WHERE table_name = 'attendance' AND column_name = 'presence'; 