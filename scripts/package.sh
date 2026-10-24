#!/usr/bin/env bash
# Empaquette l'application (backend + front) et la dépose dans votre bucket d'artefacts.
# Usage : ./scripts/package.sh <nom-du-bucket>
set -euo pipefail
cd "$(dirname "$0")/.."
BUCKET="${1:?Usage: package.sh <bucket>}"
aws s3api head-bucket --bucket "$BUCKET" 2>/dev/null || aws s3 mb "s3://$BUCKET"
rm -f /tmp/africashop-app.zip
zip -qr /tmp/africashop-app.zip backend/app backend/requirements.txt frontend -x "*/__pycache__/*"
aws s3 cp /tmp/africashop-app.zip "s3://$BUCKET/releases/africashop-app.zip"
aws s3 cp /tmp/africashop-app.zip "s3://$BUCKET/releases/africashop-app-$(date +%Y%m%d-%H%M%S).zip"
echo "OK : s3://$BUCKET/releases/africashop-app.zip"
