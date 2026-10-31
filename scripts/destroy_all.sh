#!/usr/bin/env bash
# Supprime TOUT AfricaShop (ordre inverse du déploiement) pour ne plus rien payer.
# Usage : ./scripts/destroy_all.sh
set -uo pipefail
export AWS_PAGER=""
ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
export_value() { aws cloudformation list-exports --query "Exports[?Name=='$1'].Value" --output text 2>/dev/null; }

SITE=$(export_value africashop-SiteBucketName)
MEDIA=$(export_value africashop-MediaBucketName)

echo "== Base de restauration (si elle existe) =="
if aws rds describe-db-instances --db-instance-identifier africashop-db-restore >/dev/null 2>&1; then
  aws rds delete-db-instance --db-instance-identifier africashop-db-restore --skip-final-snapshot --delete-automated-backups >/dev/null
  aws rds wait db-instance-deleted --db-instance-identifier africashop-db-restore
fi

echo "== Vidage des buckets =="
[ -n "$SITE" ]  && aws s3 rm "s3://${SITE}" --recursive --only-show-errors
[ -n "$MEDIA" ] && aws s3 rm "s3://${MEDIA}" --recursive --only-show-errors
aws s3 rb "s3://africashop-artefacts-${ACCOUNT}" --force >/dev/null 2>&1 || true

for S in monitoring edge compute data network; do
  echo "== Suppression de africashop-${S} =="
  aws cloudformation delete-stack --stack-name "africashop-${S}"
  aws cloudformation wait stack-delete-complete --stack-name "africashop-${S}"
done

echo
echo "== Vérification : tout doit être vide =="
echo "Piles actives      : $(aws cloudformation list-stacks --query "StackSummaries[?StackStatus!='DELETE_COMPLETE'&&starts_with(StackName,'africashop')].StackName" --output text)"
echo "NAT Gateways       : $(aws ec2 describe-nat-gateways --filter Name=state,Values=available,pending --query "NatGateways[].NatGatewayId" --output text)"
echo "Load balancers     : $(aws elbv2 describe-load-balancers --query "LoadBalancers[].LoadBalancerName" --output text)"
echo "Bases RDS          : $(aws rds describe-db-instances --query "DBInstances[].DBInstanceIdentifier" --output text)"
echo "IP élastiques      : $(aws ec2 describe-addresses --query "Addresses[].PublicIp" --output text)"
echo "Volumes EBS        : $(aws ec2 describe-volumes --query "Volumes[].VolumeId" --output text)"
echo "Distributions CDN  : $(aws cloudfront list-distributions --query "DistributionList.Items[].Id" --output text 2>/dev/null)"
echo "Buckets S3         : $(aws s3 ls | awk '{print $3}' | tr '\n' ' ')"
