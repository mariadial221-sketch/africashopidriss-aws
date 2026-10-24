#!/usr/bin/env bash
# Déploie le starter (1 instance EC2) dans le VPC par défaut. Usage : ./scripts/deploy_starter.sh <bucket>
set -euo pipefail
cd "$(dirname "$0")/.."
REGION="${AWS_REGION:-us-east-1}"; BUCKET="${1:?Usage: deploy_starter.sh <bucket>}"
./scripts/package.sh "$BUCKET"
VPC=$(aws ec2 describe-vpcs --region "$REGION" --filters Name=isDefault,Values=true --query "Vpcs[0].VpcId" --output text)
SUBNET=$(aws ec2 describe-subnets --region "$REGION" --filters Name=vpc-id,Values="$VPC" Name=default-for-az,Values=true --query "Subnets[0].SubnetId" --output text)
aws cloudformation deploy --region "$REGION" --stack-name africashop-starter --template-file infra/starter-ec2.yaml \
  --parameter-overrides VpcId="$VPC" SubnetId="$SUBNET" ArtifactBucket="$BUCKET" --no-fail-on-empty-changeset
aws cloudformation describe-stacks --region "$REGION" --stack-name africashop-starter \
  --query "Stacks[0].Outputs[?OutputKey=='SiteUrl'].OutputValue" --output text
echo "Patientez 2 à 3 minutes (installation au démarrage) avant d'ouvrir l'URL."
