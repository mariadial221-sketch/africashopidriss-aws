#!/usr/bin/env bash
# Déploie (ou met à jour) AfricaShop de zéro : 5 piles CloudFormation + publication du site.
# Usage   : ./scripts/deploy_all.sh <email-alertes> [limite-WAF-par-IP]
# Exemple : ./scripts/deploy_all.sh prenom.nom@exemple.com 2000
# Variable optionnelle : OWNER=<groupe> (étiquette Owner, "idrissa" par défaut).
set -euo pipefail
cd "$(dirname "$0")/.."

EMAIL="${1:?Usage: deploy_all.sh <email-alertes> [limite-WAF-par-IP]}"
RATE="${2:-2000}"
OWNER="${OWNER:-idrissa}"
export AWS_PAGER=""
START=$(date +%s)
ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
TAGS=("Project=africashop" "Owner=${OWNER}")
ARTIFACTS="africashop-artefacts-${ACCOUNT}"

log() { printf '\n== %s (+%ss) ==\n' "$1" "$(( $(date +%s) - START ))"; }
output() { aws cloudformation describe-stacks --stack-name "$1" --query "Stacks[0].Outputs[?OutputKey=='$2'].OutputValue" --output text; }

log "1/5 Réseau (VPC, sous-réseaux, NAT, groupes de sécurité)"
PL=$(aws ec2 describe-managed-prefix-lists --filters Name=prefix-list-name,Values=com.amazonaws.global.cloudfront.origin-facing --query "PrefixLists[0].PrefixListId" --output text)
[ "$PL" = "None" ] && PL=""
aws cloudformation deploy --stack-name africashop-network --template-file infra/01-network.yaml \
  --tags "${TAGS[@]}" --parameter-overrides CloudFrontPrefixListId="$PL" --no-fail-on-empty-changeset

log "2/5 Données (RDS Multi-AZ, bucket de photos)"
aws cloudformation deploy --stack-name africashop-data --template-file infra/02-data.yaml \
  --tags "${TAGS[@]}" --parameter-overrides ManagedPassword=true MultiAZ=true --no-fail-on-empty-changeset

log "3/5 Calcul (empaquetage de l'application, rôle IAM, Auto Scaling, ALB)"
./scripts/package.sh "$ARTIFACTS"
aws cloudformation deploy --stack-name africashop-compute --template-file infra/03-compute.yaml \
  --capabilities CAPABILITY_IAM --tags "${TAGS[@]}" \
  --parameter-overrides ArtifactBucket="$ARTIFACTS" TestCidr="" --no-fail-on-empty-changeset

log "4/5 Entrée (CloudFront, WAF, bucket du site)"
aws cloudformation deploy --stack-name africashop-edge --template-file infra/04-edge.yaml \
  --tags "${TAGS[@]}" --parameter-overrides EnableWaf=true RateLimit="$RATE" --no-fail-on-empty-changeset
SITE=$(output africashop-edge SiteBucketName)
aws s3 sync frontend "s3://${SITE}" --delete --cache-control no-cache --only-show-errors

log "5/5 Supervision (SNS, alarmes, tableau de bord)"
aws cloudformation deploy --stack-name africashop-monitoring --template-file infra/05-monitoring.yaml \
  --tags "${TAGS[@]}" --parameter-overrides AlertEmail="$EMAIL" --no-fail-on-empty-changeset

URL=$(output africashop-edge SiteUrl)
log "Attente du premier 200 sur ${URL}/api/info (installation des instances : 5 à 8 min)"
READY=0
for _ in $(seq 1 60); do
  code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 8 "${URL}/api/info" || true)
  if [ "$code" = "200" ]; then READY=1; break; fi
  sleep 15
done

echo
echo "Site            : ${URL}"
echo "Durée totale    : $(( ($(date +%s) - START) / 60 )) min"
if [ "$READY" = "1" ]; then
  curl -s "${URL}/api/info"; echo
  echo "Pensez à confirmer l'abonnement SNS reçu par e-mail (${EMAIL})."
else
  echo "ATTENTION : l'API ne répond pas encore. Vérifiez les cibles de l'ALB et le journal système des instances."
  exit 1
fi
