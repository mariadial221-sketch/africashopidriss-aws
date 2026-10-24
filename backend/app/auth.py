"""Authentification des vendeurs.
AUTH_MODE=none    : démo / local (toute requête est acceptée, identité "local-dev").
AUTH_MODE=cognito : jeton d'accès Cognito obligatoire (Authorization: Bearer <token>)."""
from functools import lru_cache

from fastapi import Header, HTTPException

from .config import settings


@lru_cache
def _jwks_client():
    import jwt

    url = (f"https://cognito-idp.{settings.aws_region}.amazonaws.com/"
           f"{settings.cognito_user_pool_id}/.well-known/jwks.json")
    return jwt.PyJWKClient(url)


def current_vendor_sub(authorization: str = Header(default="")) -> str:
    if settings.auth_mode != "cognito":
        return "local-dev"
    import jwt

    if not authorization.lower().startswith("bearer "):
        raise HTTPException(401, "Jeton manquant")
    token = authorization.split(" ", 1)[1]
    try:
        key = _jwks_client().get_signing_key_from_jwt(token).key
        issuer = f"https://cognito-idp.{settings.aws_region}.amazonaws.com/{settings.cognito_user_pool_id}"
        claims = jwt.decode(token, key, algorithms=["RS256"], issuer=issuer)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(401, f"Jeton invalide : {exc}") from exc
    if claims.get("token_use") != "access" or claims.get("client_id") != settings.cognito_client_id:
        raise HTTPException(401, "Jeton non destiné à cette application")
    if "vendeurs" not in claims.get("cognito:groups", []):
        raise HTTPException(403, "Réservé aux vendeurs")
    return claims["sub"]
