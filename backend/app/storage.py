"""Photos produits : le navigateur du vendeur envoie le fichier DIRECTEMENT à S3
via une URL pré-signée. Le serveur ne fait jamais transiter les octets de l'image :
il reste léger et l'upload ne consomme ni CPU ni bande passante EC2."""
import re
from pathlib import Path
from uuid import uuid4

from .config import settings

_EXT = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}


def new_key(vendor_id: str, filename: str, content_type: str) -> str:
    stem = re.sub(r"[^a-zA-Z0-9-]+", "-", Path(filename).stem).strip("-")[:40] or "photo"
    return f"products/{vendor_id}/{uuid4().hex[:12]}-{stem}.{_EXT[content_type]}"


def public_url(key: str) -> str:
    if not key:
        return ""
    if key.startswith(("http", "/")):  # URL absolue ou image statique du front (catalogue de démo)
        return key
    return f"{settings.media_public_base.rstrip('/')}/{key}"


def presign_upload(key: str, content_type: str) -> dict:
    if settings.storage_mode == "s3":
        import boto3

        s3 = boto3.client("s3", region_name=settings.aws_region)
        url = s3.generate_presigned_url(
            "put_object",
            Params={"Bucket": settings.media_bucket, "Key": key, "ContentType": content_type},
            ExpiresIn=300,  # 5 minutes : fenêtre courte = surface d'abus réduite
        )
        return {"upload_url": url, "method": "PUT", "headers": {"Content-Type": content_type}}
    # Mode local : même contrat d'API, le fichier atterrit dans ./media
    return {"upload_url": f"/api/uploads/local/{key}", "method": "PUT",
            "headers": {"Content-Type": content_type}}


def save_local(key: str, data: bytes) -> None:
    dest = Path(settings.local_media_dir) / key
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
