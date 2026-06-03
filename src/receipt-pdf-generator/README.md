# Receipt PDF Generator

Библиотека для генерации PDF чеков на Python с использованием ReportLab.

## Установка

```bash
pip install receipt-pdf-generator
```

## Быстрый старт

```python
from receipt_pdf_generator import ReceiptPDFService

# Данные чека
receipt_data = {
    'receipt_id': 12345,
    'created_at': '15.01.2024 14:30',
    'employee_name': 'Иванов Иван',
    'sales': [
        {'name': 'Хлеб', 'quantity': 2, 'price': 50},
        {'name': 'Молоко', 'quantity': 1, 'price': 80},
        {'name': 'Сыр', 'quantity': 1, 'price': 200}
    ]
}

# Генерация PDF
pdf_service = ReceiptPDFService()
pdf_buffer = pdf_service.generate_receipt_pdf(receipt_data)

# Сохранение в файл
with open('receipt.pdf', 'wb') as f:
    f.write(pdf_buffer.getvalue())
```

## Конфигурация

Можно настроить шаблон PDF:

```python
template_config = {
    'page_size': 'A4',
    'margins': {'top': 20, 'bottom': 20, 'left': 20, 'right': 20},
    'font_size': 10
}

pdf_service = ReceiptPDFService(template_config)
```