"""AfricaShop API — baseline du projet de fin de module AWS.

Lancer en local :  uvicorn app.main:app --reload
Documentation    :  http://localhost:8000/api/docs
"""
import hmac
import logging

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from . import events, storage
from .auth import current_vendor_sub
from .config import settings
from .db import Base, engine, get_db
from .models import Order, OrderLine, Product, Vendor
from .platform import instance_identity
from .schemas import (CATEGORIES, OrderIn, OrderOut, PaymentWebhookIn, PresignIn, PresignOut,
                      ProductIn, ProductOut, ProductPage, VendorIn, VendorOut)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
Base.metadata.create_all(engine)  # Phase 1 uniquement. Phase 2 : migrations Alembic.

app = FastAPI(title=settings.app_name, docs_url="/api/docs", openapi_url="/api/openapi.json")
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins.split(","),
                   allow_methods=["*"], allow_headers=["*"])

if settings.storage_mode == "local":
    import os
    os.makedirs(settings.local_media_dir, exist_ok=True)
    app.mount("/media", StaticFiles(directory=settings.local_media_dir), name="media")


def _to_out(p: Product) -> ProductOut:
    return ProductOut(id=p.id, vendor_id=p.vendor_id, vendor_name=p.vendor.name,
                      vendor_country=p.vendor.country, name=p.name, description=p.description,
                      category=p.category, price_xof=p.price_xof, stock=p.stock,
                      image_url=storage.public_url(p.image_key))


# ---------- Plateforme ----------
@app.get("/api/health", tags=["plateforme"])
def health(db: Session = Depends(get_db)):
    """Utilisé par le health check de l'ALB : vérifie aussi la base."""
    db.execute(select(1))
    return {"status": "ok"}


@app.get("/api/info", tags=["plateforme"])
def info():
    return {"app": settings.app_name, "env": settings.env, "storage": settings.storage_mode,
            "events": settings.events_mode, "auth": settings.auth_mode,
            "database": engine.dialect.name, **instance_identity()}


# ---------- Catalogue ----------
@app.get("/api/categories", tags=["catalogue"])
def categories():
    return CATEGORIES


@app.get("/api/products", response_model=ProductPage, tags=["catalogue"])
def list_products(q: str = "", category: str = "", page: int = Query(1, ge=1),
                  size: int = Query(12, ge=1, le=48), db: Session = Depends(get_db)):
    stmt = select(Product).options(joinedload(Product.vendor))
    if category:
        stmt = stmt.where(Product.category == category)
    if q:
        like = f"%{q.lower()}%"
        stmt = stmt.where(or_(func.lower(Product.name).like(like), func.lower(Product.description).like(like)))
    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    rows = db.scalars(stmt.order_by(Product.created_at.desc()).offset((page - 1) * size).limit(size)).all()
    return ProductPage(items=[_to_out(p) for p in rows], total=total or 0, page=page, size=size)


@app.get("/api/products/{product_id}", response_model=ProductOut, tags=["catalogue"])
def get_product(product_id: str, db: Session = Depends(get_db)):
    p = db.get(Product, product_id)
    if not p:
        raise HTTPException(404, "Produit introuvable")
    return _to_out(p)


# ---------- Espace vendeur ----------
@app.get("/api/vendors", response_model=list[VendorOut], tags=["vendeurs"])
def list_vendors(db: Session = Depends(get_db)):
    return db.scalars(select(Vendor).order_by(Vendor.name)).all()


@app.post("/api/vendors", response_model=VendorOut, status_code=201, tags=["vendeurs"])
def create_vendor(body: VendorIn, sub: str = Depends(current_vendor_sub), db: Session = Depends(get_db)):
    v = Vendor(**body.model_dump(), owner_sub=sub)
    db.add(v)
    db.commit()
    return v


@app.post("/api/products", response_model=ProductOut, status_code=201, tags=["vendeurs"])
def create_product(body: ProductIn, sub: str = Depends(current_vendor_sub), db: Session = Depends(get_db)):
    vendor = db.get(Vendor, body.vendor_id)
    if not vendor:
        raise HTTPException(404, "Vendeur introuvable")
    if settings.auth_mode == "cognito" and vendor.owner_sub != sub:
        raise HTTPException(403, "Ce vendeur ne vous appartient pas")
    p = Product(**body.model_dump())
    db.add(p)
    db.commit()
    db.refresh(p)
    events.publish("product.created", {"product_id": p.id, "vendor_id": vendor.id})
    return _to_out(p)


@app.post("/api/uploads/presign", response_model=PresignOut, tags=["vendeurs"])
def presign(body: PresignIn, vendor_id: str = Query(...), _sub: str = Depends(current_vendor_sub)):
    key = storage.new_key(vendor_id, body.filename, body.content_type)
    return PresignOut(key=key, public_url=storage.public_url(key),
                      **storage.presign_upload(key, body.content_type))


@app.put("/api/uploads/local/{key:path}", include_in_schema=False)
async def upload_local(key: str, request: Request):
    if settings.storage_mode != "local" or ".." in key:
        raise HTTPException(404)
    data = await request.body()
    if len(data) > 5 * 1024 * 1024:
        raise HTTPException(413, "Image > 5 Mo")
    storage.save_local(key, data)
    return {"key": key}


# ---------- Commandes & paiement ----------
@app.post("/api/orders", response_model=OrderOut, status_code=201, tags=["commandes"])
def create_order(body: OrderIn, db: Session = Depends(get_db)):
    order = Order(customer_email=body.customer_email, customer_country=body.customer_country,
                  payment_method=body.payment_method)
    total = 0
    for line in body.lines:
        p = db.get(Product, line.product_id)
        if not p:
            raise HTTPException(404, f"Produit {line.product_id} introuvable")
        if p.stock < line.quantity:
            raise HTTPException(409, f"Stock insuffisant pour « {p.name} »")
        p.stock -= line.quantity  # réservation simple ; Phase 2 : verrou / transaction SERIALIZABLE
        total += p.price_xof * line.quantity
        order.lines.append(OrderLine(product_id=p.id, quantity=line.quantity, unit_price_xof=p.price_xof))
    order.total_xof = total
    db.add(order)
    db.commit()
    events.publish("order.created", {"order_id": order.id, "total_xof": total,
                                     "email": order.customer_email, "payment_method": order.payment_method})
    return order


@app.get("/api/orders/{order_id}", response_model=OrderOut, tags=["commandes"])
def get_order(order_id: str, db: Session = Depends(get_db)):
    o = db.get(Order, order_id)
    if not o:
        raise HTTPException(404, "Commande introuvable")
    return o


@app.post("/api/payments/webhook", response_model=OrderOut, tags=["commandes"])
def payment_webhook(body: PaymentWebhookIn, x_psp_signature: str = Header(default=""),
                    db: Session = Depends(get_db)):
    """En production : le PSP signe sa notification (HMAC) et on vérifie la signature.
    En mode simulé, le front envoie le secret de démo pour illustrer le mécanisme."""
    if not hmac.compare_digest(x_psp_signature, settings.psp_webhook_secret):
        raise HTTPException(401, "Signature PSP invalide")
    o = db.get(Order, body.order_id)
    if not o:
        raise HTTPException(404, "Commande introuvable")
    if o.status != "PENDING_PAYMENT":
        return o  # idempotence : un PSP peut renvoyer la même notification plusieurs fois
    o.status = "PAID" if body.status == "SUCCEEDED" else "PAYMENT_FAILED"
    o.psp_reference = body.psp_reference
    if o.status == "PAYMENT_FAILED":
        for line in o.lines:  # libère le stock réservé
            db.get(Product, line.product_id).stock += line.quantity
    db.commit()
    events.publish(f"order.{o.status.lower()}", {"order_id": o.id, "total_xof": o.total_xof,
                                                  "email": o.customer_email})
    return o


# ---------- Servir le front sur la même origine que l'API (local et EC2 simple) ----------
# En architecture cible, le front est servi par S3 + CloudFront : mettre SERVE_FRONTEND=false.
if settings.serve_frontend:
    from pathlib import Path

    _front = Path(settings.frontend_dir) if settings.frontend_dir else Path(__file__).resolve().parents[2] / "frontend"
    if _front.is_dir():
        app.mount("/", StaticFiles(directory=_front, html=True), name="frontend")
