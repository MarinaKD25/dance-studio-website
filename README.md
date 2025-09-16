### Dance Studio — FastAPI + Vue 3 + PostgreSQL
**Дипломный проект, выполненный в рамках обучения по специальности "Информационные системы и технологии" в РГПУ им. А.И. Герцена.**

Ниже — подробное описание проекта, инструкции по установке и запуску, структура, список технологий и полезные команды.

## Описание
Веб‑приложение для танцевальной студии:
- расписание занятий, залы и преподаватели;
- учет посещаемости;
- подписки и платежи;
- роли: администратор, преподаватель, студент;
- авторизация через JWT (заголовок `token`).

Бэкенд: FastAPI + SQLModel + PostgreSQL.  
Фронтенд: Vue 3 + Axios + Vue Router + Vuex.

## Стек
- Backend: FastAPI, SQLModel, Pydantic, Passlib[bcrypt], PyJWT, python‑dotenv, psycopg2‑binary
- Frontend: Vue 3, Vue Router, Vuex, Axios
- DB: PostgreSQL

## Структура
```text
vkr/
  backend/
    add.py                # Сидер: создаёт таблицы и учебные данные
    ll1.py                # Модели SQLModel + engine (DATABASE_URL)
    main.py               # FastAPI, JWT, эндпоинты
    models.py
    requests.py
    Script_dance_studio.sql
  dance-studio-vue/
    src/
      api/index.js        # Axios + заголовок token
      router/index.js     # Роутер
      store/index.js      # Vuex
      views/...           # Страницы
      components/...      # Компоненты
    package.json
```

## Быстрый старт

### 1) Переменные окружения (.env)
Создайте файл `.env` в корне проекта:
```ini
SECRET_KEY=change_this_to_a_long_random_secret_value
DATABASE_URL=postgresql://postgres:123456789@localhost:5432/postgres
# опционально для фронтенда:
# VUE_APP_API_BASE_URL=http://127.0.0.1:8000
```
- `SECRET_KEY` — длинная случайная строка (32+ символа).
- `DATABASE_URL` — строка подключения PostgreSQL. Обновите под свою среду.

### 2) Backend
```powershell
cd vkr
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install fastapi uvicorn sqlmodel pydantic passlib[bcrypt] python-dateutil PyJWT psycopg2-binary python-dotenv
```
Инициализация БД и учебных данных:
```powershell
python backend/add.py
```
Запуск API:
```powershell
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```
API: `http://127.0.0.1:8000`

### 3) Frontend
```powershell
cd vkr/dance-studio-vue
npm install
npm run serve
```
SPA: `http://localhost:8081`  
Если API на другом адресе — обновите базовый URL в `src/api/index.js` (или используйте `VUE_APP_API_BASE_URL`).

## Авторизация и роли
- При логине сервер отдаёт JWT; фронтенд кладёт его в `localStorage` и отправляет в заголовке `token` для всех запросов.
- Бэкенд читает токен из заголовка `token`.
- Роли: `ADMIN`, `TEACHER`, `STUDENT`. Доступ к защищённым эндпоинтам проверяется на бэкенде.

## Важные эндпоинты (кратко)
- POST `/login` — получить JWT
- GET `/users/me` — текущий пользователь
- GET `/classes/` — расписание (фильтры: даты/тип/преподаватель)
- POST `/classes/` — создать занятие (ADMIN)
- PUT `/classes/{id}` — обновить занятие (ADMIN)
- DELETE `/classes/{id}` — удалить занятие (ADMIN)
- GET `/students/`, POST `/students/`, PUT `/students/{id}`, DELETE `/students/{id}` (ADMIN)
- GET `/teachers/`, POST `/admin/teachers/`, PUT `/admin/teachers/{id}`, DELETE `/admin/teachers/{id}` (ADMIN)
- POST `/classes/{class_id}/enroll` — запись студента (STUDENT)
- GET `/attendance/class/{class_id}` — посещаемость занятия
- PUT `/attendance/{attendance_id}` — обновить статус (ADMIN)
- POST `/payments/create-with-subscription` — платёж + подписка (STUDENT)
- GET `/subscriptions/{student_id}` — активные подписки

## Сидер (учебные данные)
- `backend/add.py` создаёт обезличенные пользователи/преподаватели/залы/занятия/подписки/посещаемость.
- При необходимости измените плейсхолдеры перед запуском.

## Конфигурация
- `SECRET_KEY` и `DATABASE_URL` берутся из `.env` (загружается в `main.py` и `ll1.py` через `python-dotenv`).
- Логи SQL включены (`echo=True` в `ll1.py`) для отладки — отключите на проде.

## Полезные команды
```bash
# Backend
uvicorn backend.main:app --reload

# Frontend
npm run serve
npm run build
```
## О проекте (от автора)
Данный fullstack-проект был разработан как выпускная квалификационная работа. Основная цель — создание удобной системы автоматизации процессов для современной танцевальной студии. В ходе работы были изучены и применены на практике ключевые технологии веб-разработки.
