# Déployer AfricaShop depuis zéro (CloudShell, région us-east-1)

Prérequis : un compte AWS, CloudShell ouvert dans la région **us-east-1**.

```bash
git clone https://github.com/mariadial221-sketch/africashopidriss-aws.git
cd africashopidriss-aws
chmod +x scripts/*.sh
./scripts/deploy_all.sh <votre-email> [limite-WAF]     # 30 à 45 minutes, affiche l'adresse du site à la fin
```

Le script enchaîne les cinq piles CloudFormation de `infra/` (réseau, données, calcul, entrée CloudFront + WAF,
supervision), publie le site dans son bucket privé puis attend que `/api/info` réponde.
Les ressources reçoivent les étiquettes `Project=africashop` et `Owner=<OWNER>` (variable d'environnement, "idrissa" par défaut).
Confirmez ensuite l'abonnement SNS reçu par e-mail pour recevoir les alertes.

## Vérifier

```bash
URL=$(aws cloudformation describe-stacks --stack-name africashop-edge --query "Stacks[0].Outputs[?OutputKey=='SiteUrl'].OutputValue" --output text)
curl -s $URL/api/info        # env aws, database postgresql, storage s3 ; rafraîchir : l'instance et la zone alternent
```

## Test de charge (Locust)

```bash
pip install --user locust
WAIT_MIN=0.5 WAIT_MAX=1.5 locust -f loadtest/locustfile.py --host $URL --headless -u 400 -r 20 -t 8m --csv saturation
```

Relevez le nombre d'instances, le CPU et la latence p95 dans le tableau de bord CloudWatch `africashop-dashboard`.
Pendant ce test (une seule adresse IP source), passez la limite du WAF à une valeur élevée : `./scripts/deploy_all.sh <email> 2000000`.

## Tout supprimer

```bash
./scripts/destroy_all.sh     # vide les buckets, supprime les 5 piles dans l'ordre inverse, vérifie qu'il ne reste rien
```

## Contenu

| Fichier | Rôle |
|---|---|
| `infra/01-network.yaml` | VPC, sous-réseaux, NAT, groupes de sécurité |
| `infra/02-data.yaml` | RDS PostgreSQL Multi-AZ chiffrée, bucket de photos |
| `infra/03-compute.yaml` | Rôle IAM, Auto Scaling, ALB |
| `infra/04-edge.yaml` | CloudFront, WAF, bucket du site |
| `infra/05-monitoring.yaml` | SNS, 6 alarmes, tableau de bord |
