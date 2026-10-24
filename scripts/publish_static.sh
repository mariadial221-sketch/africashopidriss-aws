#!/usr/bin/env bash
# Publie UNIQUEMENT le front sur S3 en mode simulation (aucun serveur). Usage : ./scripts/publish_static.sh <bucket>
# Le bucket doit être configuré par vous (hébergement statique ou, mieux, CloudFront + OAC).
set -euo pipefail
cd "$(dirname "$0")/../frontend"
BUCKET="${1:?Usage: publish_static.sh <bucket>}"
TMP=$(mktemp -d); cp -r . "$TMP"
sed -i 's/MODE: "auto"/MODE: "simulation"/' "$TMP/assets/js/config.js"
aws s3 sync "$TMP" "s3://$BUCKET" --delete --cache-control "no-cache"
rm -rf "$TMP"; echo "Front publié (mode simulation) dans s3://$BUCKET"
