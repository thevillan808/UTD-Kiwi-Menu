import requests
import jwt
from flask import current_app, request, g, jsonify
from functools import wraps


_jwks_cache = None


def _get_jwks():
    global _jwks_cache
    if _jwks_cache is not None:
        return _jwks_cache

    region = current_app.config.get('COGNITO_REGION')
    pool_id = current_app.config.get('COGNITO_USER_POOL_ID')
    url = f'https://cognito-idp.{region}.amazonaws.com/{pool_id}/.well-known/jwks.json'
    resp = requests.get(url, timeout=10)
    _jwks_cache = resp.json()
    return _jwks_cache


def validate_token(token):
    region = current_app.config.get('COGNITO_REGION')
    pool_id = current_app.config.get('COGNITO_USER_POOL_ID')
    client_id = current_app.config.get('COGNITO_APP_CLIENT_ID')
    issuer = f'https://cognito-idp.{region}.amazonaws.com/{pool_id}'

    jwks = _get_jwks()
    header = jwt.get_unverified_header(token)
    kid = header.get('kid')

    key_data = None
    for k in jwks.get('keys', []):
        if k['kid'] == kid:
            key_data = k
            break

    if key_data is None:
        raise jwt.InvalidTokenError('Public key not found in JWKS')

    public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key_data)
    claims = jwt.decode(
        token,
        public_key,
        algorithms=['RS256'],
        audience=client_id,
        issuer=issuer,
    )
    return claims


def require_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Forbidden', 'detail': 'Missing or invalid token'}), 403
        token = auth_header[len('Bearer '):]
        try:
            claims = validate_token(token)
        except Exception:
            return jsonify({'error': 'Forbidden', 'detail': 'Invalid or expired token'}), 403
        g.current_user = claims.get('cognito:username') or claims.get('sub')
        return f(*args, **kwargs)
    return wrapper
