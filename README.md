# AfricaShop Starter — application de simulation du projet AWS

Petite boutique en ligne **de simulation** (catalogue, panier, paiement simulé, espace vendeur avec
photo) qui sert de point de départ au projet AfricaShop. L'application est volontairement simple :
**le sujet, c'est l'infrastructure que vous allez construire autour.**

## Lancer toute la plateforme avec Docker Compose (recommandé)

```bash
cp .env.example .env            # puis changez le mot de passe
docker compose up -d --build    # http://localhost:8080
docker compose ps               # db, 2 répliques api, web
docker compose logs -f api      # journaux des deux répliques
docker compose down             # arrêt (ajoutez -v pour effacer base et photos)
```

Le stack local reproduit en miniature l'architecture AWS visée :

| Conteneur | Rôle | Équivalent AWS |
|---|---|---|
| `web` (nginx) | Sert le site, les photos, et répartit `/api/*` entre les répliques | CloudFront + Application Load Balancer |
| `api` × 2 | API FastAPI sans état | Instances EC2 d'un Auto Scaling group |
| `db` (PostgreSQL 17) | Base de données | Amazon RDS for PostgreSQL |
| volume `media` | Photos des vendeurs | Bucket S3 |
| `adminer` (profil `outils`) | Explorer la base : `docker compose --profile outils up -d` → :8081 | — |

Expériences à faire : rafraîchir la page et regarder le bandeau changer de conteneur ;
`docker compose up -d --scale api=4` ; `docker compose stop db` puis observer `/api/health` ;
`docker compose kill api` sur une réplique et vérifier que le site répond toujours.

## Autres façons de la faire tourner

| Mode | Ce qu'il faut | À quoi ça sert |
|---|---|---|
| **Simulation** (navigateur seul) | Un bucket S3 (ou `python3 -m http.server`) | Hébergement statique S3 / CloudFront. Données dans le navigateur (localStorage). |
| **Starter EC2** | `scripts/deploy_starter.sh <bucket>` | Point de départ naïf dans AWS : 1 instance publique, SQLite, photos sur disque. |
| **Votre architecture** | Vos templates IaC | ALB + Auto Scaling, RDS, S3… activés par variables d'environnement. |

Le bandeau en haut de chaque page affiche le mode actif, la base utilisée et **l'instance (ou le
conteneur) et l'AZ qui ont répondu**.

## Développement sans Docker

```bash
cd frontend && python3 -m http.server 5500          # mode simulation
cd backend && python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
python -m app.seed && uvicorn app.main:app --reload # http://localhost:8000 (doc API : /api/docs)
pytest -q
```

## Illustrations

Les visuels du catalogue (tissus wax, kente, bogolan, vannerie, karité…) sont des **illustrations
SVG originales** générées par `tools/gen_images.py` : aucune image sous droits. Pour utiliser de
vraies photos, publiez des produits depuis l'espace vendeur ou remplacez les fichiers de
`frontend/assets/img/products/` (même nom).

## Variables d'environnement de l'API (aucune modification de code nécessaire)

| Variable | Défaut | Valeur en architecture cible | Service AWS |
|---|---|---|---|
| `DB_HOST` + `DB_SECRET_ARN` | vide → SQLite | endpoint RDS + ARN du secret | Amazon RDS PostgreSQL + Secrets Manager |
| `STORAGE_MODE`, `MEDIA_BUCKET` | `local` | `s3`, nom du bucket photos | Amazon S3 (upload par URL pré-signée) |
| `MEDIA_PUBLIC_BASE` | `/media` | `/media` (servi par CloudFront) ou URL du bucket | CloudFront |
| `EVENTS_MODE`, `SNS_TOPIC_ARN` | `log` | `sns`, ARN du topic | Amazon SNS (bonus) |
| `AUTH_MODE` | `none` | `cognito` (+ `COGNITO_USER_POOL_ID`, `COGNITO_CLIENT_ID`) | Amazon Cognito (bonus M1) |
| `SERVE_FRONTEND` | `true` | `false` si le front est sur S3 + CloudFront | — |
| `APP_ENV` | `local` | `aws` | — |

Points d'API utiles à l'infrastructure : `GET /api/health` (vérifie aussi la base, pour le health
check de l'ALB) et `GET /api/info` (instance, AZ, modes actifs).

## Learner Lab

Région us-east-1, rôles imposés (`LabRole`, `LabInstanceProfile`), crédit limité :
**supprimez vos stacks en fin de séance** (`aws cloudformation delete-stack ...`).

## Faiblesses du starter (à corriger et à expliquer dans votre dossier)

1. Une seule instance, une seule AZ : la moindre panne coupe le site.
2. Instance dans un sous-réseau public, port 80 ouvert sur Internet, pas de HTTPS.
3. Base SQLite **sur le disque de l'instance** : deux instances = deux bases différentes ; instance perdue = données perdues.
4. Photos sur le disque local : mêmes problèmes, et les octets passent par le serveur.
5. Aucune sauvegarde, aucune alarme, aucun tableau de bord.
6. Paiement simulé : le front connaît le secret de démonstration (`PSP_DEMO_SECRET`, identique à
   `PSP_WEBHOOK_SECRET`) et peut « payer » seul une commande.
   En production, seul le prestataire de paiement signe la notification.
7. `LabInstanceProfile` donne beaucoup plus de droits que nécessaire : rédigez la politique moindre privilège.
