"""Jeu de données de démonstration : python -m app.seed"""
from sqlalchemy import select, text
from sqlalchemy.orm import Session


from .db import Base, engine
from .models import Product, Vendor

VENDORS = [
    ("Atelier Soumbédioune", "SN", "Dakar"),
    ("Coopérative Karité de Koudougou", "BF", "Koudougou"),
    ("Pagnes & Wax Treichville", "CI", "Abidjan"),
    ("Bogolan de Ségou", "ML", "Ségou"),
]
PRODUCTS = [
    (0, "Boubou brodé homme", "vetements", 45000, "Bazin riche brodé main, coupe ample.", "boubou"),
    (0, "Panier tressé de Thiès", "artisanat", 12000, "Fibres de rônier, tressage traditionnel.", "panier-thies"),
    (0, "Café Touba moulu 500 g", "epicerie", 3500, "Café parfumé au poivre de Guinée (djar).", "cafe-touba"),
    (1, "Beurre de karité brut 250 g", "cosmetiques", 4500, "Non raffiné, coopérative de femmes.", "karite"),
    (1, "Savon noir au karité", "cosmetiques", 2000, "Saponifié à froid, sans parfum ajouté.", "savon-noir"),
    (2, "Robe en wax", "vetements", 38000, "Coupe évasée, coton 100 %.", "robe-wax"),
    (2, "Sac cabas en pagne", "artisanat", 15000, "Doublure coton, anses renforcées.", "cabas-pagne"),
    (3, "Plaid bogolan 150x200", "maison", 55000, "Teinture à la boue fermentée, motifs Ségou.", "plaid-bogolan"),
    (3, "Coussin bogolan", "maison", 9000, "Housse amovible, motif tortue.", "coussin-bogolan"),
    (0, "Bissap séché 250 g", "epicerie", 2500, "Fleurs d'hibiscus de Kaolack.", "bissap"),
    (1, "Huile de baobab 100 ml", "cosmetiques", 6500, "Pressée à froid, peaux sèches.", "huile-baobab"),
    (2, "Masque Gouro décoratif", "artisanat", 27000, "Bois sculpté, finition patinée.", "masque"),
]


def run() -> None:
    # Une seule transaction : verrou -> création des tables -> données.
    # Plusieurs conteneurs / instances démarrent en même temps : le verrou PostgreSQL évite les doublons.
    with engine.begin() as conn:
        if conn.dialect.name == "postgresql":
            conn.execute(text("SELECT pg_advisory_xact_lock(4242)"))
        Base.metadata.create_all(conn)
        with Session(bind=conn) as db:
            if db.scalar(select(Vendor).limit(1)):
                print("Données déjà présentes : rien à faire.")
                return
            vendors = [Vendor(name=n, country=c, city=v) for n, c, v in VENDORS]
            db.add_all(vendors)
            db.flush()
            for vi, name, cat, price, desc, slug in PRODUCTS:
                db.add(Product(vendor_id=vendors[vi].id, name=name, category=cat, price_xof=price,
                               description=desc, stock=25, image_key=f"/assets/img/products/{slug}.svg"))
            db.flush()
            print(f"{len(vendors)} vendeurs et {len(PRODUCTS)} produits créés.")


if __name__ == "__main__":
    run()
