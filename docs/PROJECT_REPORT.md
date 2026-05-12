# Отчет по проекту "Web Shop" - Система управления магазином

**Разработчик:** Мясников Вадим  
**Дата:** май 2026 г.  
**Язык:** Python (FastAPI), JavaScript  
**СУБД:** SQLite

---

## 1. Описание целевой аудитории и типовые задачи

### Целевая аудитория:
- **Собственники магазинов** - администраторы системы, управляющие правами доступа сотрудников
- **Менеджеры товаров** - сотрудники, отвечающие за пополнение каталога товаров и управление категориями
- **Кассиры/Продавцы** - сотрудники, осуществляющие продажу товаров и оформление чеков
- **Руководители отделов** - сотрудники, имеющие право назначать подчиненных
- **Главный менеджер** - администратор со всеми правами доступа

### Типовые задачи:
1. **Управление товарами:**
   - Добавление новых товаров в каталог
   - Организация товаров по категориям
   - Мониторинг запасов на складе
   - Установка цен на товары

2. **Управление сотрудниками:**
   - Регистрация новых сотрудников системы
   - Назначение должностей и ролей
   - Управление правами доступа (разделение по ролям)
   - Назначение начальника для каждого сотрудника

3. **Обработка продаж:**
   - Оформление чеков покупок
   - Запись продаж товаров
   - Автоматическое уменьшение запасов на складе
   - Просмотр истории всех продаж

4. **Контроль доступа:**
   - Аутентификация сотрудников через логин/пароль
   - Управление правами: продажа, добавление товаров, добавление категорий, редактирование товаров, добавление должностей, добавление начальников
   - Система JWT-токенов для безопасности

---

## 2. Существующие аналоги на рынке ПО

### Конкурентные решения:

| Аналог | СУБД | Архитектура | Функциональные возможности |
|--------|------|------------|--------------------------|
| **1С:УТП** | Собственная БД | Монолитная десктопная | Полный учет товаров, многоскладской учет, интеграция с 1С |
| **OpenCart** | MySQL/PostgreSQL | MVC (PHP) | E-commerce, управление товарами, интеграция платежей |
| **Shopify** | Облачная БД | SaaS облачная | Полнофункциональный магазин, маркетинг, аналитика |
| **Odoo POS** | PostgreSQL | Модульная (Python) | POS система, управление складом, CRM интеграция |
| **Square for Retail** | Облачная | Mobile-first | POS для малых бизнесов, аналитика в реальном времени |

### Преимущества нашего решения:
- **Легкость в развертывании** - Docker контейнеризация
- **Простота интеграции** - REST API
- **Гибкость ролевой системы** - настраиваемые права доступа
- **Минимальные требования** - может работать на скромном сервере
- **Открытый исходный код** - возможность кастомизации

---

## 3. Описание реализуемого процесса в нотациях

### 3.1 Диаграмма основного процесса продажи:

![](https://i.ibb.co/4w1wpH62/Gemini-Generated-Image-qalrfjqalrfjqalr.png)

### 3.2 Диаграмма аутентификации и управления правами:

![](https://i.ibb.co/SD3NpLPq/Gemini-Generated-Image-z6s13sz6s13sz6s1.png)

---

## 4. Схема данных 

![](https://i.ibb.co/Y7pxtpr9/image.png)

---
## 5. Структура БД в PostgreSQL

Отправленно в forlabs

---

## 6. Скрин интерфейса
![](https://i.ibb.co/nqL8C9Sq/image.png)
![](https://i.ibb.co/nqL8C9Sq/image.png)
![](https://i.ibb.co/39tb3mPx/image.png)
![](https://i.ibb.co/BVcPfjgP/image.png)
![](https://i.ibb.co/8LD903PL/image.png)
![](https://i.ibb.co/Fbysy3Ny/image.png)
![](https://i.ibb.co/XktK82NG/image.png)

---

## 7. SQL запросы для основных операций

### 7.1 Получение всех товаров с категориями:
```sql
SELECT 
    p.id,
    p.name AS product_name,
    p.price,
    p.quantity_at_storage,
    c.name AS category_name
FROM products p
JOIN categories c ON p.id_category = c.id
ORDER BY p.id;
```

### 7.2 Получение всех чеков с информацией о продавце:
```sql
SELECT 
    r.id,
    r.created_at,
    e.name AS employee_name,
    e.surname AS employee_surname,
    e.login
FROM receipts r
JOIN employees e ON r.id_employee = e.id
ORDER BY r.created_at DESC;
```

### 7.3 Получение всех продаж с деталями товара и чека:
```sql
SELECT 
    s.id,
    s.quintity AS quantity,
    p.name AS product_name,
    p.price,
    (s.quintity * p.price) AS total_sum,
    r.created_at,
    e.name AS employee_name
FROM sales s
JOIN products p ON s.id_product = p.id
JOIN receipts r ON s.id_receipt = r.id
JOIN employees e ON r.id_employee = e.id
ORDER BY r.created_at DESC;
```

### 7.4 Получение сотрудника с его должностью и правами доступа:
```sql
SELECT 
    e.id,
    e.name,
    e.surname,
    e.login,
    j.name AS job_name,
    r.make_sales,
    r.add_categories,
    r.add_products,
    r.redact_products,
    r.add_jobs,
    r.add_boss
FROM employees e
JOIN jobs j ON e.id_job = j.id
JOIN roots r ON j.root_id = r.id
WHERE e.login = 'ivan.petrov'
LIMIT 1;
```

### 7.5 Статистика по продажам за период:
```sql
SELECT 
    DATE(r.created_at) AS date,
    COUNT(DISTINCT r.id) AS number_of_receipts,
    COUNT(s.id) AS total_sales,
    SUM(s.quintity * p.price) AS total_revenue
FROM receipts r
LEFT JOIN sales s ON r.id = s.id_receipt
LEFT JOIN products p ON s.id_product = p.id
WHERE r.created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(r.created_at)
ORDER BY date DESC;
```

### 7.6 Товары с низким уровнем запаса (менее 5 единиц):
```sql
SELECT 
    p.id,
    p.name,
    c.name AS category,
    p.price,
    p.quantity_at_storage
FROM products p
JOIN categories c ON p.id_category = c.id
WHERE p.quantity_at_storage < 5
ORDER BY p.quantity_at_storage ASC;
```

### 7.7 Создание нового чека и добавление продажи:
```sql
-- Начало транзакции
BEGIN;

-- 1. Создать новый чек
INSERT INTO receipts (created_at, id_employee)
VALUES (CURRENT_TIMESTAMP, 1)
RETURNING id;

-- 2. Добавить продажу товара
INSERT INTO sales (id_receipt, id_product, quintity)
VALUES (1, 5, 2);

-- 3. Уменьшить количество товара на складе
UPDATE products
SET quantity_at_storage = quantity_at_storage - 2
WHERE id = 5 AND quantity_at_storage >= 2;

-- Фиксировать изменения
COMMIT;
```

### 7.8 Получение данных сотрудника и его подчиненных:
```sql
SELECT 
    CASE 
        WHEN e.boss IS NULL THEN 'Руководитель'
        ELSE 'Подчиненный'
    END AS type,
    e.id,
    e.name,
    e.surname,
    e.login,
    j.name AS job_name
FROM employees e
JOIN jobs j ON e.id_job = j.id
WHERE e.boss = 1 OR e.id = 1
ORDER BY e.boss, e.id;
```

### 7.9 Добавление новой категории товаров:
```sql
INSERT INTO categories (name)
VALUES ('Электроника')
RETURNING id, name;
```

### 7.10 Добавление нового продукта:
```sql
INSERT INTO products (name, price, id_category, quantity_at_storage)
VALUES (
    'Ноутбук Dell XPS',
    89999,
    5,
    3
)
RETURNING id, name, price, quantity_at_storage;
```

### 7.11 Регистрация нового сотрудника (с хешированием пароля в приложении):
```sql
INSERT INTO employees (name, surname, login, password, id_job)
VALUES (
    'Александр',
    'Новиков',
    'alex.novikov',
    '$2b$12$...',  -- BCrypt хешированный пароль
    3
)
RETURNING id, name, surname, login, id_job;
```

### 7.12 Получение всех должностей с соответствующими правами:
```sql
SELECT 
    j.id,
    j.name AS job_name,
    r.make_sales,
    r.add_categories,
    r.add_products,
    r.redact_products,
    r.add_jobs,
    r.add_boss
FROM jobs j
JOIN roots r ON j.root_id = r.id
ORDER BY j.id;
```

---
