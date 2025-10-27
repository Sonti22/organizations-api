# Примеры использования Organizations API

## 🔐 Аутентификация

Все запросы требуют заголовок `X-API-Key`:

```bash
X-API-Key: dev-api-key-12345
```

---

## 🏢 Organizations (Организации)

### 1. Получить все организации

```bash
curl -H "X-API-Key: dev-api-key-12345" \
  http://localhost:8000/api/v1/organizations
```

**Response:**
```json
{
  "items": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "name": "ООО \"Рога и Копыта\"",
      "phones": ["+7-923-666-13-13", "2-222-222"],
      "building_id": "...",
      "building": {
        "id": "...",
        "address": "г. Новосибирск, ул. Блюхера 32/1",
        "latitude": 55.0415,
        "longitude": 82.9346
      },
      "activities": [
        {
          "id": "...",
          "name": "Молочная продукция",
          "path": "001.002",
          "level": 2
        }
      ]
    }
  ],
  "total": 100,
  "page": 1,
  "size": 50
}
```

### 2. Организации в конкретном здании

```bash
curl -H "X-API-Key: dev-api-key-12345" \
  "http://localhost:8000/api/v1/organizations?building_id=123e4567-e89b-12d3-a456-426614174000"
```

### 3. Получить организацию по ID

```bash
curl -H "X-API-Key: dev-api-key-12345" \
  http://localhost:8000/api/v1/organizations/123e4567-e89b-12d3-a456-426614174000
```

### 4. Создать организацию

```bash
curl -X POST \
  -H "X-API-Key: dev-api-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "ООО \"Тестовая компания\"",
    "phones": ["+7-923-111-22-33", "8-800-555-35-35"],
    "building_id": "123e4567-e89b-12d3-a456-426614174000",
    "activity_ids": ["abc-...", "def-..."]
  }' \
  http://localhost:8000/api/v1/organizations
```

### 5. Обновить организацию

```bash
curl -X PUT \
  -H "X-API-Key: dev-api-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "ООО \"Новое название\"",
    "phones": ["+7-999-888-77-66"]
  }' \
  http://localhost:8000/api/v1/organizations/123e4567-e89b-12d3-a456-426614174000
```

### 6. Удалить организацию

```bash
curl -X DELETE \
  -H "X-API-Key: dev-api-key-12345" \
  http://localhost:8000/api/v1/organizations/123e4567-e89b-12d3-a456-426614174000
```

---

## 🔍 Поиск организаций

### 7. Поиск по названию

```bash
curl -H "X-API-Key: dev-api-key-12345" \
  "http://localhost:8000/api/v1/organizations/search/name?query=Рога"
```

### 8. Организации по виду деятельности (без вложенных)

```bash
curl -H "X-API-Key: dev-api-key-12345" \
  "http://localhost:8000/api/v1/organizations/by-activity/abc-123?include_nested=false"
```

### 9. Организации по виду деятельности (с вложенными)

**Пример:** Поиск по "Еда" (level 1) → найдутся все организации с "Мясная продукция", "Молочная продукция" (level 2-3)

```bash
curl -H "X-API-Key: dev-api-key-12345" \
  "http://localhost:8000/api/v1/organizations/by-activity/food-activity-id?include_nested=true"
```

---

## 🌍 Геопространственный поиск

### 10. Организации в радиусе

**Пример:** Найти все организации в радиусе 5 км от точки

```bash
curl -H "X-API-Key: dev-api-key-12345" \
  "http://localhost:8000/api/v1/organizations/geo/radius?latitude=55.0415&longitude=82.9346&radius_meters=5000"
```

**Параметры:**
- `latitude`: Широта центра (-90 до 90)
- `longitude`: Долгота центра (-180 до 180)
- `radius_meters`: Радиус в метрах (макс 100000 = 100 км)

### 11. Организации в прямоугольной области (bbox)

**Пример:** Найти организации в bounding box

```bash
curl -H "X-API-Key: dev-api-key-12345" \
  "http://localhost:8000/api/v1/organizations/geo/bbox?min_lat=55.0&max_lat=55.1&min_lon=82.9&max_lon=83.0"
```

**Параметры:**
- `min_lat`, `max_lat`: Диапазон широты
- `min_lon`, `max_lon`: Диапазон долготы

---

## 🏗️ Buildings (Здания)

### 12. Получить все здания

```bash
curl -H "X-API-Key: dev-api-key-12345" \
  http://localhost:8000/api/v1/buildings
```

### 13. Получить здание по ID

```bash
curl -H "X-API-Key: dev-api-key-12345" \
  http://localhost:8000/api/v1/buildings/123e4567-e89b-12d3-a456-426614174000
```

### 14. Создать здание

```bash
curl -X POST \
  -H "X-API-Key: dev-api-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "address": "г. Москва, ул. Ленина 1, офис 3",
    "latitude": 55.7558,
    "longitude": 37.6173
  }' \
  http://localhost:8000/api/v1/buildings
```

### 15. Обновить здание

```bash
curl -X PUT \
  -H "X-API-Key: dev-api-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "address": "г. Москва, ул. Ленина 1, офис 5"
  }' \
  http://localhost:8000/api/v1/buildings/123e4567-e89b-12d3-a456-426614174000
```

---

## 🌳 Activities (Деятельности)

### 16. Получить все деятельности

```bash
curl -H "X-API-Key: dev-api-key-12345" \
  http://localhost:8000/api/v1/activities
```

### 17. Фильтр по уровню

```bash
curl -H "X-API-Key: dev-api-key-12345" \
  "http://localhost:8000/api/v1/activities?level=1"
```

### 18. Получить дерево деятельностей

```bash
curl -H "X-API-Key: dev-api-key-12345" \
  http://localhost:8000/api/v1/activities/tree
```

**Response:**
```json
[
  {
    "id": "...",
    "name": "Еда",
    "path": "001",
    "level": 1,
    "parent_id": null,
    "children": [
      {
        "id": "...",
        "name": "Мясная продукция",
        "path": "001.001",
        "level": 2,
        "parent_id": "...",
        "children": [
          {
            "id": "...",
            "name": "Оптовая торговля",
            "path": "001.001.001",
            "level": 3,
            "parent_id": "...",
            "children": []
          }
        ]
      }
    ]
  }
]
```

### 19. Создать корневую деятельность (level 1)

```bash
curl -X POST \
  -H "X-API-Key: dev-api-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Новая деятельность",
    "parent_id": null
  }' \
  http://localhost:8000/api/v1/activities
```

### 20. Создать дочернюю деятельность

```bash
curl -X POST \
  -H "X-API-Key: dev-api-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Дочерняя деятельность",
    "parent_id": "parent-activity-id"
  }' \
  http://localhost:8000/api/v1/activities
```

**Ограничение:** Максимальная глубина дерева = 3 уровня

---

## 📄 Пагинация

Все list endpoints поддерживают пагинацию:

```bash
curl -H "X-API-Key: dev-api-key-12345" \
  "http://localhost:8000/api/v1/organizations?page=2&size=20"
```

**Параметры:**
- `page`: Номер страницы (начиная с 1)
- `size`: Количество элементов на странице (макс 100)

---

## 🏥 Health Check

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "ok",
  "app": "Organizations API",
  "version": "1.0.0"
}
```

---

## 📚 Документация API

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json

---

## 🧪 Примеры с httpie

### Установка httpie

```bash
pip install httpie
```

### Примеры

```bash
# GET
http GET localhost:8000/api/v1/organizations X-API-Key:dev-api-key-12345

# POST
http POST localhost:8000/api/v1/buildings \
  X-API-Key:dev-api-key-12345 \
  address="г. Москва, ул. Тверская 1" \
  latitude:=55.7558 \
  longitude:=37.6173

# Geo search
http GET localhost:8000/api/v1/organizations/geo/radius \
  X-API-Key:dev-api-key-12345 \
  latitude==55.0415 \
  longitude==82.9346 \
  radius_meters==5000
```

---

## 🐍 Примеры с Python

```python
import requests

API_URL = "http://localhost:8000/api/v1"
API_KEY = "dev-api-key-12345"
HEADERS = {"X-API-Key": API_KEY}

# Получить организации
response = requests.get(f"{API_URL}/organizations", headers=HEADERS)
organizations = response.json()

# Создать здание
building_data = {
    "address": "г. Москва, ул. Тверская 1",
    "latitude": 55.7558,
    "longitude": 37.6173,
}
response = requests.post(f"{API_URL}/buildings", json=building_data, headers=HEADERS)
building = response.json()

# Geo search
params = {
    "latitude": 55.0415,
    "longitude": 82.9346,
    "radius_meters": 5000,
}
response = requests.get(f"{API_URL}/organizations/geo/radius", params=params, headers=HEADERS)
nearby_orgs = response.json()
```

---

## ⚠️ Коды ошибок

| Код | Описание |
|-----|----------|
| 200 | OK |
| 201 | Created |
| 204 | No Content (Delete success) |
| 400 | Bad Request (validation error) |
| 401 | Unauthorized (invalid API key) |
| 404 | Not Found |
| 422 | Unprocessable Entity (validation) |
| 500 | Internal Server Error |

---

## 📞 Поддержка

**GitHub:** https://github.com/Sonti22/organizations-api

**Email:** suren6pro@gmail.com

