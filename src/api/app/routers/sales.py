from fastapi import APIRouter, Depends, HTTPException, status
from api.app.schemas import schemas
from api.app.db.queries import Queries
from datetime import datetime
from typing import Optional
from api.app.dependencies import create_session
from sqlalchemy.orm import Session
from api.app.routers.auth import get_current_user
from api.app.core.security import get_permissions
from receipt_pdf_generator import ReceiptPDFGenerator
from fastapi.responses import StreamingResponse
from api.app.services.emailSenderService import EmailSender as email_sender
import api.app.core.exceptions as exceptions   

sales = APIRouter(tags=["sales"])


@sales.post("/products/")
def insert_product(
    name: str,
    price: int,
    id_category: int,
    quantity_at_storage: int,
    session: Session = Depends(create_session),
    permissions: schemas.PermissionSchema = Depends(get_permissions),
) -> dict:
    if permissions.add_products:
        Queries.insert_product(name, price, id_category, quantity_at_storage, session)
        return {"message": "success"}
    else:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="You can't do this")


@sales.post("/categories/")
def insert_category(
    name: str,
    session: Session = Depends(create_session),
    permissions: schemas.PermissionSchema = Depends(get_permissions),
) -> dict:
    if permissions.add_categories:
        Queries.insert_category(name, session)
        return {"message": "success"}
    else:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="You can't do this")


@sales.get("/products/", response_model=list[schemas.ProductSchema])
def all_products(session: Session = Depends(create_session)):
    products_orm = Queries.all_products(session)
    products_schema = [schemas.ProductSchema.model_validate(row) for row in products_orm]
    return products_schema


@sales.post("/jobs/", response_model=schemas.JobSchema)
def insert_job(
    name: str,
    permission_id: int,
    session: Session = Depends(create_session),
):
    job_orm = Queries.insert_job(name, permission_id, session)
    job_schema = schemas.JobSchema.model_validate(job_orm)
    return job_schema


@sales.post("/receipts/", response_model=schemas.ReceiptSchema)
def create_receipt(
    created_at: datetime,
    user: schemas.UserPublicSchema = Depends(get_current_user),
    session: Session = Depends(create_session),
):
    receipt = Queries.create_receipt(created_at=created_at, id_employee=user.id, session=session)
    return schemas.ReceiptSchema.model_validate(receipt)


@sales.post("/sales/")
def insert_sale(
    id_product: int,
    quantity: int,
    receipt_id: int,
    session: Session = Depends(create_session),
    permissions: schemas.PermissionSchema = Depends(get_permissions),
):
    try:
        if permissions.make_sales:
            Queries.insert_sale_with_storage_check(id_product, quantity, receipt_id, session)
            return {"message": "success"}
        else:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="You can't do this")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Something went wrong"
        )


@sales.get("/categories/", response_model=list[schemas.CategorySchema])
def all_categories(session: Session = Depends(create_session)):
    categories_orm = Queries.all_categories(session)
    categories_schema = [schemas.CategorySchema.model_validate(row) for row in categories_orm]
    return categories_schema


@sales.get("/jobs/", response_model=list[schemas.JobSchema])
def all_jobs(session: Session = Depends(create_session)):
    jobs_orm = Queries.all_jobs(session)
    jobs_schema = [schemas.JobSchema.model_validate(row) for row in jobs_orm]
    return jobs_schema


@sales.get("/receipts/", response_model=list[schemas.ReceiptSchema])
def all_receipts(session: Session = Depends(create_session)):
    receipts_orm = Queries.all_receipts(session)
    receipts_schema = [schemas.ReceiptSchema.model_validate(row) for row in receipts_orm]
    return receipts_schema


@sales.get("/employees/", response_model=list[schemas.UserPublicSchema])
def all_employees(session: Session = Depends(create_session)):
    employees_orm = Queries.all_employees(session)
    employees_schema = [schemas.UserPublicSchema.model_validate(row) for row in employees_orm]
    return employees_schema


@sales.get("/sales/", response_model=list[schemas.SaleSchema])
def all_sales(session: Session = Depends(create_session)):
    sales_orm = Queries.all_sales(session)
    sales_schema = [schemas.SaleSchema.model_validate(row) for row in sales_orm]
    return sales_schema


@sales.patch("/employees/")
def add_boss(
    id: int,
    boss_id: int,
    session: Session = Depends(create_session),
    permissions: schemas.PermissionSchema = Depends(get_permissions),
):
    if permissions.add_boss:
        Queries.add_boss(id, boss_id, session)
        return {"message": "success"}
    else:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="You can't do this")


@sales.patch("/products/")
def update_product(
    product_id: int,
    price: Optional[int] = None,
    quantity_at_storage: Optional[int] = None,
    session: Session = Depends(create_session),
    permissions: schemas.PermissionSchema = Depends(get_permissions),
):
    if permissions.add_products:
        Queries.update_product(product_id, price, quantity_at_storage, session)
        return {"message": "success"}
    else:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="You can't do this")


# ИСПРАВЛЕННЫЙ ЭНДПОИНТ delete_product
@sales.delete("/products/")
def delete_product(
    id: int,
    session: Session = Depends(create_session),
    permissions: schemas.PermissionSchema = Depends(get_permissions),
):
    if not permissions.add_products:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="You can't do this")
    
    try:
        result = Queries.delete_product(id, session)
        return result
    except exceptions.NotFoundError as e:
        raise HTTPException(status_code=e.code, detail=e.message)


@sales.get("/products/{id}", response_model=schemas.ProductSchema)
def product_by_id(
    id: int,
    session: Session = Depends(create_session),
    permissions: schemas.PermissionSchema = Depends(get_permissions),
):
    return Queries.get_product_by_id(id, session)


@sales.get("/products/filter/", response_model=list[schemas.ProductSchema])
def filtered_products(
    category_id: int | None,
    min_price: float = 0,
    max_price: float = 10**8,
    session: Session = Depends(create_session),
    permissions: schemas.PermissionSchema = Depends(get_permissions),
):
    products_orm = Queries.filtered_products(category_id, min_price, max_price, session)
    products_schema = [schemas.ProductSchema.model_validate(row) for row in products_orm]
    return products_schema


@sales.get("/products/category/", response_model=list[schemas.ProductSchema])
def products_by_category(
    category_id: int,
    session: Session = Depends(create_session),
    permissions: schemas.PermissionSchema = Depends(get_permissions),
):
    products_orm = Queries.products_by_category(category_id, session)
    products_schema = [schemas.ProductSchema.model_validate(row) for row in products_orm]
    return products_schema


@sales.get("/employee/{id}/sales", response_model=list[schemas.SaleSchema])
def employee_sales(
    id: int,
    session: Session = Depends(create_session),
    permissions: schemas.PermissionSchema = Depends(get_permissions),
):
    sales_orm = Queries.employee_sales(id, session)
    sales_schema = [schemas.SaleSchema.model_validate(row) for row in sales_orm]
    return sales_schema


@sales.get("/sales/filter/", response_model=list[schemas.SaleSchema])
def sales_products(
    min_sum: int | None = None,
    max_sum: int | None = None,
    min_date: datetime | None = None,
    max_date: datetime | None = None,
    product_id: int | None = None,
    employee_id: int | None = None,
    session: Session = Depends(create_session),
    permissions: schemas.PermissionSchema = Depends(get_permissions),
):

    sales_orm = Queries.filtered_sales(
        session, min_sum, max_sum, min_date, max_date, product_id, employee_id
    )
    sales_schema = [schemas.SaleSchema.model_validate(row) for row in sales_orm]
    return sales_schema


@sales.post("/permissions/")
def add_permission(
    permisions: schemas.PermissionSchema,
    session: Session = Depends(create_session),
    permissions: schemas.PermissionSchema = Depends(get_permissions),
):
    permission_orm = Queries.insert_permission(
        permisions.make_sales,
        permisions.add_categories,
        permisions.add_products,
        permisions.redact_products,
        permisions.add_jobs,
        permisions.add_boss,
        session,
    )
    return schemas.PermissionSchema.model_validate(permission_orm)


@sales.get("/permissions/", response_model=list[schemas.PermissionSchema])
def all_permissions(session: Session = Depends(create_session)):
    permissions_orm = Queries.get_all_permissions(session)
    permissions_schema = [schemas.PermissionSchema.model_validate(row) for row in permissions_orm]
    return permissions_schema


@sales.get("/sales/receipt/{id_receipt}", response_model=list[schemas.SaleSchema])
def sales_by_receipt(id_receipt: int, session: Session = Depends(create_session)):
    sales_orm = Queries.sales_by_receipt(id_receipt, session)
    sales_schema = [schemas.SaleSchema.model_validate(row) for row in sales_orm]
    return sales_schema


@sales.get("/products/to/buy", response_model=list[schemas.ProductSchema])
def products_to_buy(
    red_quantity: int,
    session: Session = Depends(create_session),
    permissions: schemas.PermissionSchema = Depends(get_permissions),
):
    if permissions.add_products:
        products_orm = Queries.products_to_buy(red_quantity, session)
        product_schema = [schemas.ProductSchema.model_validate(row) for row in products_orm]
        return product_schema
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can't do this")

@sales.get("/{receipt_id}/pdf")
async def get_receipt_pdf(
    receipt_id: int,
    session: Session = Depends(create_session),
    current_user: schemas.UserPublicSchema = Depends(get_current_user),
)->StreamingResponse:
    try:
        receipt_orm = Queries.sales_by_receipt(receipt_id, session)
        
        if not receipt_orm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Чек с ID {receipt_id} не найден"
            )
        
        receipt = receipt_orm[0].receipt
        employee = receipt.employee
        
        pdf_data = {
            'receipt_id': receipt.id,
            'created_at': receipt.created_at.strftime('%d.%m.%Y %H:%M'),
            'employee_name': f"{employee.name} {employee.surname}",
            'sales': []
        }
        
        total_sum = 0
        for sale in receipt_orm:
            product = sale.product
            line_sum = product.price * sale.quantity
            total_sum += line_sum
            
            pdf_data['sales'].append({
                'name': product.name,
                'quantity': sale.quantity,
                'price': product.price
            })
        
        pdf_data['total_sum'] = total_sum
        
        pdf_buffer = ReceiptPDFGenerator().generate_receipt_pdf(pdf_data)
        
        filename = f"receipt_{receipt_id}.pdf"
        
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )
    
@sales.post("/send/{receipt_id}")
async def send_receipt(
    receipt_id: int,
    email_address: str,
    session: Session = Depends(create_session),
    current_user: schemas.UserPublicSchema = Depends(get_current_user),
) -> dict:
    """
    Отправка PDF чека на указанный email
    
    Args:
        receipt_id: ID чека
        email_address: Email для отправки
        session: Сессия БД
        current_user: Текущий пользователь
        pdf_service: PDF сервис
        
    Returns:
        dict: Статус отправки
    """
    try:
        if "@" not in email_address or "." not in email_address:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверный формат email адреса"
            )
        
        receipt_orm = Queries.sales_by_receipt(receipt_id, session)
        
        if not receipt_orm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Чек с ID {receipt_id} не найден"
            )
        
        receipt = receipt_orm[0].receipt
        employee = receipt.employee
        
        pdf_data = {
            'receipt_id': receipt.id,
            'created_at': receipt.created_at.strftime('%d.%m.%Y %H:%M'),
            'employee_name': f"{employee.name} {employee.surname}",
            'sales': []
        }
        
        total_sum = 0
        for sale in receipt_orm:
            product = sale.product
            line_sum = product.price * sale.quantity
            total_sum += line_sum
            
            pdf_data['sales'].append({
                'name': product.name,
                'quantity': sale.quantity,
                'price': product.price
            })
        
        pdf_data['total_sum'] = total_sum
        
        # Генерируем PDF
        pdf_buffer = ReceiptPDFGenerator().generate_receipt_pdf(pdf_data)
        pdf_data_bytes = pdf_buffer.getvalue()
        
        # Формируем email
        subject = f"Чек №{receipt_id} от {pdf_data['created_at']}"
        body = f"""Здравствуйте!

Присылаем вам чек №{receipt_id} от {pdf_data['created_at']}.

Магазин: Ваш Магазин
Продавец: {pdf_data['employee_name']}

С уважением,
Команда Вашего Магазина
"""
        
        # Отправляем email
        email_filename = f"receipt_{receipt_id}.pdf"
        email_sent = email_sender.send_email(
            to_email=email_address,
            subject=subject,
            body=body,
            attachment_data=pdf_data_bytes,
            attachment_name=email_filename
        )
        
        if not email_sent:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Не удалось отправить email"
            )
        
        return {
            "message": "Чек успешно отправлен на email",
            "receipt_id": receipt_id,
            "email": email_address,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )
