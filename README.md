# 📦 **Web‑Shop** – Интернет‑магазин с API, PDF‑чеками и Docker‑развёртыванием

> **Кратко:** этот учебный проект представляет собой систему управления магазином с API на FastAPI, базой данных на SQLAlchemy, Docker-контейнеризацией и переиспользуемой библиотекой для генерации PDF чеков.

---

## 🎯 Что реализовано

| Функциональность | Описание |
|------------------|----------|
| **Аутентификация** | Регистрация, логин, JWT‑токены |
| **Управление товаром** | CRUD‑операции над товарами и категориями |
| **Продажи** | Создание чеков, добавление продаж, проверка остатков |
| **PDF‑чек** | Генерация PDF‑чека через отдельную библиотеку `receipt-pdf-generator` |
| **Отправка чека на email** | Мок‑сервис отправляет PDF‑чек по указанному адресу |
| **Менеджмент** | Управление сотрудниками, просмотр продаж подчинённых |
| **Docker‑развёртывание** | `Dockerfile`, `compose.yaml`, единственная точка входа |
| **Тесты** | Юнит‑ и интеграционные тесты (pytest) |
| **Документация** | README, архитектурные схемы (Mermaid), API‑описание |
| **Автоматизация** | `Makefile` с командами `install`, `test`, `run`, `build`, `format` и др. |

---

## 📂 Структура репозитория

```
.
├── src/
│   └── api/
|       ├── Dockerfile           # Сборка контейнера API
|       ├── tests/                    # Тесты проекта (FastAPI)
│       └── app/
│           ├── main.py          # Точка входа (uvicorn)
│           ├── core/            # config, security, exceptions
│           ├── db/              # queries, setup (SQLAlchemy)
|           ├── models/          # SQLAlchemy models
│           ├── routers/         # auth, manager, sales
|           ├── services/        # mockEmailSender
│           ├── schemas/         # pydantic‑схемы
│           └── dependencies.py   # create_session
├── src/receipt-pdf-generator/   # Переиспользуемая библиотека
│   └── src/receipt_pdf_generator/
│       ├── __init__.py
│       ├── __version__.py
│       └── services/
│           └── receipt_pdf_service.py
├── docs/                     # Архитектурные и пользовательские документы
│   ├── architecture.md
│   ├── api.md
│   └── diagrams/
│       ├── use-case.md
│       ├── sequence.md
│       └── deployment.md
├── compose.yaml              # Docker‑Compose (api + nginx)
├── Makefile                  # Обычные команды проекта
├── pyproject.toml            # Метаданные, зависимости
├── .gitignore
└── README.md                 
```

---

## ⚙️ Быстрый запуск (Docker – **рекомендованный** способ)

> **Требования:** Docker ≥ 24, Docker‑Compose ≥ 2

1. **Клонировать репозиторий**

   ```bash
   git clone https://github.com/zpenr/web-shop.git
   cd web-shop
   ```

2. **Подготовить переменные окружения**

   ```bash
   make create-env
   # при необходимости откорректировать .env
   ```
3. **Создать ключи для JWT**
```bash
make create-kyes
```
4. **Запустить всё в контейнерах**

   ```bash
   make build   # собирает образы и поднимает API + nginx
   ```

5. **Проверить, что сервис работает**

   ```bash
   curl http://localhost:8080/   # отдаст index.html (frontend)
   curl http://localhost:8000/auth/me/ -H "Authorization: Bearer <token>"
   ```

6. **Остановить и очистить**

   ```bash
   make stop
   ```

---

## 🚀 Запуск без Docker

> **Требования:** Python 3.12, `virtualenv` (рекомендовано)

```bash
# 1 Создать виртуальное окружение
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 2 Установить зависимости
pip install -e .[dev]       # зависимости для разработки (pytest, …)

# 3 Подготовить переменные окружения
make create-env
# при необходимости откорректировать .env

# 4 Создать ключи для JWT

make create-kyes

# 5 Запустить сервер
uvicorn src.api.app.main:app --reload --host 0.0.0.0 --port 8000
```

Откройте <http://localhost:8000/docs> – интерактивная Swagger‑документация FastAPI.

---

## 🧪 Тестирование

### Запуск всех тестов

```bash
make test
```

### Запуск только юнит‑тестов

```bash
make unit-tests
```

### Запуск только интеграционных

```bash
make integration-tests
```

---

## 📚 Документация

* **`docs/diagrams/`** – диаграммы:  
  * `use-case.md` – роли (Клиент, Менеджер, Администратор) и их функции.  
  * `sequence.md` – последовательность создания чека, генерации PDF и отправки email.  

Собрать HTML‑документацию (Sphinx) – `make docs`.

---

## 🏗️ Автоматизация (Makefile)

| Команда | Описание |
|---------|----------|
| `make test` | Запустить pytest с покрытием |
| `make unit-tests` | Запуск только юнит‑тестов |
| `make integration-tests` | Запуск только интеграционных |
| `make run` | `uvicorn src.api.app.main:app` (dev‑режим) |
| `make format` | Форматировать код `black` |
| `make lint` | Lint `flake8` |
| `make mypy` | Проверка типов `mypy` |
| `make docs` | сгенерировать sphinx документацию `docs/` |
| `make build` / `stop` | Управление контейнерами |
| `make create-kyes` | Создать ключи для JWT |
| `make create-env` | Создать окружение с параметрами по умолчанию |
---

## 📦 Переиспользуемый компонент – **receipt‑pdf‑generator**

### Установка

```bash
pip install receipt-pdf-generator
```

### Пример использования

```python
from receipt_pdf_generator import ReceiptPDFService

receipt_data = {
    "receipt_id": 123,
    "created_at": "15.01.2024 14:30",
    "employee_name": "Иванов Иван",
    "sales": [
        {"name": "Хлеб", "quantity": 2, "price": 50},
        {"name": "Молоко", "quantity": 1, "price": 80},
    ],
}

pdf_service = ReceiptPDFService()
pdf_bytes = pdf_service.generate_receipt_pdf(receipt_data)

with open("receipt.pdf", "wb") as f:
    f.write(pdf_bytes.getvalue())
```

> **NOTE:** библиотека упакована в отдельный `src/receipt-pdf-generator` и опубликована (см. `pyproject.toml` → `tool.poetry`). При необходимости её можно опубликовать в TestPyPI.

---

## 📄 Лицензия

Этот проект распространяется под лицензией **MIT** – смотрите файл [LICENSE](LICENSE).

---

## 📞 Контакты

- **Автор:** Myasnikov Vadim  
- **E‑mail:** [zpenr@bk.ru](mailto:zpenr@bk.ru)  
- **GitHub:** <https://github.com/zpenr/web-shop>  

- **Автор:** Vitalik 
- **E‑mail:** [green.ta1e10@gmail.com](mailto:green.ta1e10@gmail.com)  
- **GitHub:** <https://github.com/vit0lik>  

- **Автор:** Elizarev Mihail  