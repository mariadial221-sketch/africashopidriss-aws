"""Test de charge AfricaShop (Locust).

    pip install locust
    locust -f loadtest/locustfile.py --host https://<votre-url> --headless -u 300 -r 20 -t 10m --csv resultats
    WAIT_MIN=0.5 WAIT_MAX=1.5 locust -f loadtest/locustfile.py --host https://<votre-url> --headless -u 400 -r 20 -t 8m --csv saturation

Profil : majorité de navigation catalogue (cacheable), un peu de fiches produit, rares commandes.
Observez pendant le test : CPU de l'ASG, nombre d'instances, latence p95 de l'ALB, connexions RDS.
"""
import os
import random

from locust import HttpUser, between, task


class Visiteur(HttpUser):
    # Temps de réflexion (le « W » de la loi de Little). Réglable sans modifier le fichier :
    #   WAIT_MIN=0.5 WAIT_MAX=1.5 locust ...   (test de saturation)   -   par défaut 5 à 20 s (visiteur réaliste)
    wait_time = between(float(os.getenv("WAIT_MIN", "5")), float(os.getenv("WAIT_MAX", "20")))

    def on_start(self):
        r = self.client.get("/api/products?size=48", name="/api/products")
        self.ids = [p["id"] for p in r.json().get("items", [])] if r.ok else []

    @task(8)
    def catalogue(self):
        cat = random.choice(["", "vetements", "artisanat", "cosmetiques", "epicerie", "maison"])
        self.client.get(f"/api/products?category={cat}", name="/api/products")

    @task(4)
    def fiche(self):
        if self.ids:
            self.client.get(f"/api/products/{random.choice(self.ids)}", name="/api/products/[id]")

    @task(1)
    def commande(self):
        if not self.ids:
            return
        r = self.client.post("/api/orders", name="/api/orders", json={
            "customer_email": "test@africashop.sn", "customer_country": "SN", "payment_method": "mobile_money",
            "lines": [{"product_id": random.choice(self.ids), "quantity": 1}]})
        if r.status_code == 201:
            self.client.post("/api/payments/webhook", name="/api/payments/webhook",
                             headers={"X-PSP-Signature": "dev-secret"},
                             json={"order_id": r.json()["id"], "psp_reference": "LOAD", "status": "SUCCEEDED"})
