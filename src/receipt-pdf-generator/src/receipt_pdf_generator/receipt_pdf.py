# src/receipt_pdf_generator/services/receipt_pdf_service.py
from io import BytesIO
from typing import List, Optional
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm


class ReceiptPDFGenerator:
    
    def __init__(self, template_config: Optional[dict] = None):
        """
        :param template_config: Конфигурация шаблона PDF
        """
        self.config = template_config or {}
        self.styles = getSampleStyleSheet()
        
    def generate_receipt_pdf(self, receipt_data: dict) -> BytesIO:
        """
        Сгенерировать PDF чек
        
        :param receipt_data: Словарь с данными чека
        :return: BytesIO с PDF файлом
        """
        buffer = BytesIO()
        
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=A4,
            rightMargin=20*mm, 
            leftMargin=20*mm,
            topMargin=20*mm, 
            bottomMargin=20*mm
        )

        elements = self._generate_receipt_elements(receipt_data)
        doc.build(elements)
        buffer.seek(0)
        return buffer
    
    def _generate_receipt_elements(self, data: dict):
        """Генерация элементов PDF документа"""
        elements = []
        
        # Заголовок
        elements.append(Paragraph(f"<b>ЧЕК №{data['receipt_id']}</b>", self.styles["Title"]))
        elements.append(Spacer(1, 10*mm))

        # Информация о покупке
        info_data = [
            ["Дата:", data.get('created_at', 'N/A')],
            ["Продавец:", data.get('employee_name', 'N/A')],
            ["ID чека:", str(data.get('receipt_id', ''))],
        ]
        
        elements.append(self._create_table(info_data))
        elements.append(Spacer(1, 8*mm))

        # Таблица покупок
        table_data = [["Товар", "Кол-во", "Цена", "Сумма"]]
        total_sum = 0

        for sale in data.get('sales', []):
            line_sum = sale['price'] * sale['quantity']
            total_sum += line_sum
            table_data.append([
                sale['name'],
                str(sale['quantity']),
                f"{sale['price']} ₽",
                f"{line_sum} ₽"
            ])

        # Итог
        table_data.append(["", "", "ИТОГО:", f"{total_sum} ₽"])
        elements.append(self._create_table(table_data))

        elements.append(Spacer(1, 15*mm))
        elements.append(Paragraph("Спасибо за покупку!", self.styles["Normal"]))

        return elements
    
    def _create_table(self, data: List[List[str]]) -> Table:
        """Создать стилизованную таблицу"""
        table = Table(data, colWidths=[70*mm, 25*mm, 30*mm, 35*mm])
        table.setStyle(TableStyle([
            # Заголовок
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            # Данные
            ("FONTNAME", (0, 1), (-1, -2), "Helvetica"),
            ("FONTSIZE", (0, 1), (-1, -2), 9),
            ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
            # Итог
            ("FONTNAME", (-1, -1), (-1, -1), "Helvetica-Bold"),
            ("FONTSIZE", (-1, -1), (-1, -1), 11),
            ("LINEABOVE", (0, -1), (-1, -1), 1, colors.black),
            # Общее
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
        ]))
        return table


if __name__ == "__main__":
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
    
    pdf_service = ReceiptPDFGenerator()
    pdf_buffer = pdf_service.generate_receipt_pdf(receipt_data)
    
    with open('receipt.pdf', 'wb') as f:
        f.write(pdf_buffer.getvalue())
    
    print("PDF чек сгенерирован!")