"""Product management API endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.dependencies import get_db
from backend.models import Category, Product, ProductSize
from backend.schemas import ProductCreate, ProductListResponse, ProductResponse, ProductUpdate

router = APIRouter()


def _build_product_response(product: Product) -> ProductResponse:
    response = ProductResponse.model_validate(product)
    if product.category:
        return response.model_copy(update={"category_name": product.category.name})
    return response


@router.get("", response_model=ProductListResponse)
def list_products(
    category_id: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
) -> ProductListResponse:
    query = db.query(Product)

    if category_id:
        query = query.filter(Product.category_id == category_id)
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))

    products = query.order_by(Product.name).all()
    return ProductListResponse(data=[_build_product_response(product) for product in products])


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
) -> ProductResponse:
    existing = db.query(Product).filter(Product.id == product.id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": f"Product with ID '{product.id}' already exists",
                "code": "DUPLICATE_ID",
                "details": None,
            },
        )

    if product.category_id:
        category = db.query(Category).filter(Category.id == product.category_id).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error": f"Category with ID '{product.category_id}' not found",
                    "code": "VALIDATION_ERROR",
                    "details": {"field": "category_id"},
                },
            )

    db_product = Product(
        id=product.id,
        name=product.name,
        price=product.price,
        category_id=product.category_id,
        created_at=product.created_at,
    )
    db.add(db_product)

    for size in product.sizes:
        db.add(
            ProductSize(
                id=size.id,
                product_id=product.id,
                name=size.name,
                price=size.price,
                sort_order=size.sort_order,
            )
        )

    db.commit()
    db.refresh(db_product)
    return _build_product_response(db_product)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: str,
    db: Session = Depends(get_db),
) -> ProductResponse:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": f"Product with ID '{product_id}' not found",
                "code": "NOT_FOUND",
                "details": None,
            },
        )

    return _build_product_response(product)


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: str,
    product_update: ProductUpdate,
    db: Session = Depends(get_db),
) -> ProductResponse:
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": f"Product with ID '{product_id}' not found",
                "code": "NOT_FOUND",
                "details": None,
            },
        )

    if product_update.name is not None:
        db_product.name = product_update.name
    if product_update.price is not None:
        db_product.price = product_update.price

    if product_update.category_id is not None:
        if product_update.category_id:
            category = (
                db.query(Category)
                .filter(Category.id == product_update.category_id)
                .first()
            )
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail={
                        "error": f"Category with ID '{product_update.category_id}' not found",
                        "code": "VALIDATION_ERROR",
                        "details": {"field": "category_id"},
                    },
                )
        db_product.category_id = product_update.category_id

    if product_update.sizes is not None:
        db.query(ProductSize).filter(ProductSize.product_id == product_id).delete()
        for size in product_update.sizes:
            db.add(
                ProductSize(
                    id=size.id,
                    product_id=product_id,
                    name=size.name,
                    price=size.price,
                    sort_order=size.sort_order,
                )
            )

    db.commit()
    db.refresh(db_product)
    return _build_product_response(db_product)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: str,
    db: Session = Depends(get_db),
) -> None:
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": f"Product with ID '{product_id}' not found",
                "code": "NOT_FOUND",
                "details": None,
            },
        )

    db.delete(db_product)
    db.commit()
    return None
