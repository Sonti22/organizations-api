# Инструкция по развёртыванию Organizations API

## 📋 Требования

### Минимальные требования:

- **Docker** 20.10+ и **Docker Compose** 2.0+
- **OR** Python 3.11+ + PostgreSQL 15+ + PostGIS 3.4+
- **OR** Poetry 1.7+ для локальной разработки

---

## 🚀 Вариант 1: Docker Compose (рекомендуется)

### Шаг 1: Клонирование репозитория

```bash
git clone https://github.com/Sonti22/organizations-api.git
cd organizations-api
```

### Шаг 2: Создание .env файла

```bash
cp .env.example .env
```

**Важно!** Измените `API_KEY` в `.env` для production:

```env
API_KEY=your-secure-api-key-here
```

### Шаг 3: Запуск контейнеров

```bash
docker-compose up --build -d
```

Это запустит:
- PostgreSQL 15 + PostGIS 3.4 (порт 5432)
- FastAPI приложение (порт 8000)

### Шаг 4: Применение миграций

```bash
docker-compose exec app alembic upgrade head
```

### Шаг 5: Загрузка тестовых данных

```bash
docker-compose exec app python -m app.db.seed
```

### Шаг 6: Проверка

Откройте в браузере:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health: http://localhost:8000/health

---

## 🛠️ Вариант 2: Локальная разработка

### Шаг 1: Установка зависимостей

#### С Poetry (рекомендуется):

```bash
# Установить Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Установить зависимости
poetry install
```

#### С pip:

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt  # Создайте из pyproject.toml
```

### Шаг 2: Запуск PostgreSQL + PostGIS

```bash
docker run -d \
  --name postgres-postgis \
  -e POSTGRES_DB=organizations \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  postgis/postgis:15-3.4
```

### Шаг 3: Создание .env

```bash
cp .env.example .env
```

Измените `DATABASE_URL` на локальный:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/organizations
```

### Шаг 4: Применение миграций

```bash
poetry run alembic upgrade head
```

### Шаг 5: Загрузка тестовых данных

```bash
poetry run python -m app.db.seed
```

### Шаг 6: Запуск сервера

```bash
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🧪 Тестирование

### Unit и Integration тесты

```bash
# С Poetry
poetry run pytest

# С покрытием
poetry run pytest --cov=app --cov-report=html

# Только определённые тесты
poetry run pytest tests/test_api.py -v
```

### Создание тестовой БД

```bash
# PostgreSQL
createdb -U postgres organizations_test

# Или через Docker
docker exec -it postgres-postgis psql -U postgres -c "CREATE DATABASE organizations_test;"
```

---

## 📊 Миграции базы данных

### Создание новой миграции

```bash
poetry run alembic revision --autogenerate -m "описание изменений"
```

### Применение миграций

```bash
poetry run alembic upgrade head
```

### Откат миграции

```bash
poetry run alembic downgrade -1
```

### История миграций

```bash
poetry run alembic history
```

---

## 🔧 Production настройки

### 1. Переменные окружения

Измените в `.env`:

```env
DEBUG=false
API_KEY=super-secure-random-key-12345
DATABASE_URL=postgresql+asyncpg://user:pass@db-host:5432/organizations
RELOAD=false
LOG_LEVEL=warning
```

### 2. Gunicorn + Uvicorn workers

```bash
pip install gunicorn

gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

### 3. Nginx reverse proxy

```nginx
server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 4. SSL (Let's Encrypt)

```bash
sudo certbot --nginx -d api.example.com
```

---

## 🐳 Docker Production

### Dockerfile (оптимизированный)

Используйте multi-stage build из `Dockerfile`.

### Docker Compose Production

```yaml
version: '3.9'

services:
  postgres:
    image: postgis/postgis:15-3.4
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always

  app:
    build: .
    environment:
      DATABASE_URL: postgresql+asyncpg://postgres:password@postgres:5432/organizations
      API_KEY: ${API_KEY}
      DEBUG: false
    depends_on:
      - postgres
    ports:
      - "8000:8000"
    restart: always

volumes:
  postgres_data:
```

### Запуск в production

```bash
docker-compose -f docker-compose.prod.yml up -d
```

---

## 🔍 Мониторинг и логирование

### Логи Docker

```bash
docker-compose logs -f app
docker-compose logs -f postgres
```

### Health check

```bash
curl http://localhost:8000/health
```

### Metrics (опционально)

Добавить Prometheus endpoints:

```python
from prometheus_client import make_asgi_app

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
```

---

## 🛑 Остановка и очистка

### Остановка контейнеров

```bash
docker-compose down
```

### Очистка с удалением volumes

```bash
docker-compose down -v
```

### Полная очистка

```bash
docker-compose down -v --rmi all
```

---

## 🔐 Безопасность

### Checklist:

- [x] Изменить API_KEY на случайный ключ
- [x] Использовать HTTPS в production
- [x] Ограничить доступ к PostgreSQL (firewall)
- [x] Регулярно обновлять зависимости
- [x] Настроить rate limiting
- [x] Логировать все запросы
- [x] Бэкапы базы данных

### Генерация секретного ключа

```python
import secrets
print(secrets.token_urlsafe(32))
```

---

## 📞 Поддержка

**Issues:** https://github.com/Sonti22/organizations-api/issues

**Email:** suren6pro@gmail.com

**Stack:** FastAPI, SQLAlchemy, PostgreSQL, PostGIS, Docker

