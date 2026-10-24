import os
import tempfile

os.environ["DATABASE_URL"] = f"sqlite:///{tempfile.mkdtemp()}/test.db"
os.environ["LOCAL_MEDIA_DIR"] = tempfile.mkdtemp()

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from app.seed import run as seed  # noqa: E402

seed()
client = TestClient(app)
SIG = {"X-PSP-Signature": "dev-secret"}


def test_health_and_info():
    assert client.get("/api/health").json() == {"status": "ok"}
    assert client.get("/api/info").json()["database"] == "sqlite"


def test_catalogue_search_and_filter():
    page = client.get("/api/products", params={"category": "cosmetiques"}).json()
    assert page["total"] == 3 and all(p["category"] == "cosmetiques" for p in page["items"])
    assert client.get("/api/products", params={"q": "karité"}).json()["total"] >= 2


def test_vendor_creates_product_with_photo():
    v = client.post("/api/vendors", json={"name": "Test Shop", "country": "SN", "city": "Thiès"}).json()
    pre = client.post("/api/uploads/presign", params={"vendor_id": v["id"]},
                      json={"filename": "Mon Panier!.jpg", "content_type": "image/jpeg"}).json()
    assert pre["key"].startswith(f"products/{v['id']}/") and pre["key"].endswith(".jpg")
    assert client.put(pre["upload_url"], content=b"\xff\xd8fake", headers=pre["headers"]).status_code == 200
    p = client.post("/api/products", json={"vendor_id": v["id"], "name": "Panier", "category": "artisanat",
                                           "price_xof": 10000, "stock": 3, "image_key": pre["key"]})
    assert p.status_code == 201 and p.json()["image_url"] == f"/media/{pre['key']}"
    assert client.get(p.json()["image_url"]).status_code == 200


def test_order_payment_flow_is_idempotent_and_releases_stock():
    prod = client.get("/api/products").json()["items"][0]
    o = client.post("/api/orders", json={"customer_email": "a@b.sn", "customer_country": "SN",
                                         "payment_method": "mobile_money",
                                         "lines": [{"product_id": prod["id"], "quantity": 2}]}).json()
    assert o["status"] == "PENDING_PAYMENT" and o["total_xof"] == prod["price_xof"] * 2
    assert client.get(f"/api/products/{prod['id']}").json()["stock"] == prod["stock"] - 2
    bad = client.post("/api/payments/webhook", json={"order_id": o["id"], "psp_reference": "x",
                                                      "status": "SUCCEEDED"}, headers={"X-PSP-Signature": "nope"})
    assert bad.status_code == 401
    r = client.post("/api/payments/webhook", json={"order_id": o["id"], "psp_reference": "PSP-1",
                                                    "status": "FAILED"}, headers=SIG).json()
    assert r["status"] == "PAYMENT_FAILED"
    assert client.get(f"/api/products/{prod['id']}").json()["stock"] == prod["stock"]
    again = client.post("/api/payments/webhook", json={"order_id": o["id"], "psp_reference": "PSP-1",
                                                        "status": "SUCCEEDED"}, headers=SIG).json()
    assert again["status"] == "PAYMENT_FAILED"


def test_stock_and_validation_errors():
    prod = client.get("/api/products").json()["items"][0]
    r = client.post("/api/orders", json={"customer_email": "a@b.sn", "customer_country": "SN",
                                         "payment_method": "card",
                                         "lines": [{"product_id": prod["id"], "quantity": 50}]})
    assert r.status_code == 409
    assert client.post("/api/orders", json={"customer_email": "pas-un-email", "customer_country": "SN",
                                            "payment_method": "card", "lines": []}).status_code == 422
