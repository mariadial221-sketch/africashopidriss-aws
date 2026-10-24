"""Identité de l'instance via IMDSv2 : permet de VOIR le répartiteur de charge travailler
(rafraîchir /api/info et constater que l'instance / l'AZ change)."""
import os
import socket
import urllib.request
from functools import lru_cache

_IMDS = "http://169.254.169.254/latest"


def _imds(path: str, token: str) -> str:
    req = urllib.request.Request(f"{_IMDS}/meta-data/{path}", headers={"X-aws-ec2-metadata-token": token})
    with urllib.request.urlopen(req, timeout=0.3) as r:
        return r.read().decode()


@lru_cache
def instance_identity() -> dict:
    env = os.getenv("APP_ENV", "local")
    if env == "local":
        return {"instance_id": "local", "az": "local", "host": socket.gethostname()}
    if env == "docker":  # le nom d'hôte du conteneur montre quelle réplique a répondu
        return {"instance_id": f"conteneur {socket.gethostname()[:12]}", "az": "docker", "host": socket.gethostname()}
    try:
        req = urllib.request.Request(f"{_IMDS}/api/token", method="PUT",
                                     headers={"X-aws-ec2-metadata-token-ttl-seconds": "300"})
        with urllib.request.urlopen(req, timeout=0.3) as r:
            token = r.read().decode()
        return {"instance_id": _imds("instance-id", token),
                "az": _imds("placement/availability-zone", token),
                "host": socket.gethostname()}
    except Exception:  # noqa: BLE001 - conteneur ECS, Lambda...
        return {"instance_id": "n/a", "az": "n/a", "host": socket.gethostname()}
