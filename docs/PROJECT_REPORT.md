## 1. Назначение ветки dev

Ветка `dev` содержит актуальные доработки проекта **Web Shop**, которые ещё не влиты в `master`. Она предназначена для тестирования новых функций, интеграции изменений и стабилизации перед релизом.

### Основные отличия от master

| Компонент | master | dev |
|-----------|--------|-----|
| Права доступа | Таблица `roots`, поле `root_id` в `jobs` | Таблица `permissions`, поле `permission_id` |
| Генерация PDF | Отсутствует | Добавлен эндпоинт `GET /{receipt_id}/pdf` |
| Отправка email | Отсутствует | Заглушка `EmailSender` + эндпоинт `POST /send/{receipt_id}` |
| Тесты | Базовые | Расширенные (граничные случаи, исключения, удаление несуществующих записей) |
| Обработка ошибок | Частичная | Добавлено исключение `NotFoundError` (404) при удалении товара |

---

## 2. Новый функционал ветки dev

### 2.1 Переименование `roots` → `permissions`

Для улучшения читаемости кода таблица `roots` переименована в `permissions`, а внешний ключ `root_id` в `jobs` переименован в `permission_id`. Миграции (`c8d9e0f1a2b3_rename_roots_to_permissions.py`) отрабатывают автоматически.

**Затронутые файлы:**
- `models.py`: класс `Permission` вместо `Roots`
- `schemas.py`: `PermissionSchema`
- `queries.py`: все методы с `permission`
- `security.py`: `get_permissions`

### 2.2 Генерация PDF-чеков

Добавлен эндпоинт `GET /{receipt_id}/pdf`, который генерирует PDF-чек с использованием библиотеки `receipt-pdf-generator`.

**Пример запроса:**
```bash
curl -X GET "http://localhost:8000/123/pdf" -H "Authorization: Bearer <token>" --output receipt.pdf
```
### 2.3 Отправка PDF на email

Эндпоинт `POST /send/{receipt_id}` принимает параметр `email_address` и отправляет сгенерированный PDF на указанный email. В текущей реализации используется заглушка `EmailSender.send_email()`, которая всегда возвращает `True` (для интеграции с реальным SMTP нужно заменить на реальную логику).

**Пример запроса:**

```bash
curl -X POST "http://localhost:8000/send/123?email_address=user@example.com" -H "Authorization: Bearer <token>"

ответ:
{
  "message": "Чек успешно отправлен на email",
  "receipt_id": 123,
  "email": "user@example.com",
  "timestamp": "2026-06-05T10:00:00"
}
```
### 2.4 Улучшенная обработка ошибок

1. Добавлено исключение NotFoundError (код 404) в exceptions.py.

2. В методе Queries.delete_product теперь проверяется существование товара; если товар не найден, выбрасывается NotFoundError.

3. Эндпоинт DELETE /products/ обрабатывает это исключение и возвращает HTTP 404 с сообщением.

### 2.5 Расширенные тесты

- В tests/test_queries.py добавлены тесты на граничные случаи:

- удаление несуществующего товара (test_delete_product_nonexistent_raises_not_found)

- обновление товара с нулевой ценой и отрицательным количеством

- фильтрация товаров с пустым результатом

- создание сотрудника с дублирующимся логином (ожидается IntegrityError)

- назначение начальника для несуществующего сотрудника
