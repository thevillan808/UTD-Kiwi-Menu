import logging
import time
import base64
import json
import requests
from flask import current_app, request, g, jsonify
from functools import wraps
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers

logger = logging.getLogger(__name__)

# Cache keyed by issuer URL
_jwks_cache = {}


def _b64url_decode(s):
    """Base64url decode with automatic padding."""
    s = s.replace('-', '+').replace('_', '/')
    padding = 4 - len(s) % 4
    return base64.b64decode(s + '=' * (padding % 4))


def _decode_part(s):
    return json.loads(_b64url_decode(s))


def _get_jwks_for_issuer(issuer_url):
    if issuer_url in _jwks_cache:
        return _jwks_cache[issuer_url]
    url = f'{issuer_url}/.well-known/jwks.json'
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    _jwks_cache[issuer_url] = resp.json()
    return _jwks_cache[issuer_url]


def _public_key_from_jwk(jwk):
    n = int.from_bytes(_b64url_decode(jwk['n']), 'big')
    e = int.from_bytes(_b64url_decode(jwk['e']), 'big')
    return RSAPublicNumbers(e, n).public_key(default_backend())


def validate_token(token):
    parts = token.split('.')
    if len(parts) != 3:
        raise ValueError('Invalid JWT structure')

    header = _decode_part(parts[0])
    payload = _decode_part(parts[1])

    # Check expiry
    if payload.get('exp', 0) < time.time():
        raise ValueError('Token has expired')

    # Security: only accept tokens from Cognito
    issuer = payload.get('iss', '')
    if 'cognito-idp' not in issuer or 'amazonaws.com' not in issuer:
        raise ValueError('Issuer is not a trusted Cognito pool')

    # Check issuer claim matches iss
    if payload.get('iss') != issuer:
        raise ValueError('Issuer mismatch')

    # Check audience
    client_id = current_app.config.get('COGNITO_APP_CLIENT_ID')
    if client_id:
        aud = payload.get('aud')
        allowed = aud if isinstance(aud, list) else [aud]
        if client_id not in allowed:
            raise ValueError(f'Audience mismatch: expected {client_id}, got {aud}')

    # Fetch JWKS and find matching key
    jwks = _get_jwks_for_issuer(issuer)
    kid = header.get('kid')
    key_data = next((k for k in jwks.get('keys', []) if k['kid'] == kid), None)
    if key_data is None:
        raise ValueError('Public key not found in JWKS')

    # Verify RSA-SHA256 signature using cryptography library
    public_key = _public_key_from_jwk(key_data)
    message = f'{parts[0]}.{parts[1]}'.encode('ascii')
    signature = _b64url_decode(parts[2])
    public_key.verify(signature, message, asym_padding.PKCS1v15(), hashes.SHA256())

    return payload


def _provision_user(username):
    """Auto-create a local DB record for a Cognito user on first login."""
    try:
        from app.db import db
        from app.models.User import User
        if not db.session.get(User, username):
            user = User(username=username, password='cognito', firstname=username,
                        lastname='', balance=10000.0)
            db.session.add(user)
            db.session.commit()
            logger.info('Auto-provisioned new user: %s', username)
    except Exception:
        logger.exception('Failed to auto-provision user %s', username)
        try:
            from app.db import db
            db.session.rollback()
        except Exception:
            pass


def require_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Forbidden', 'detail': 'Missing or invalid token'}), 403
        token = auth_header[len('Bearer '):]
        try:
            claims = validate_token(token)
        except Exception as e:
            logger.exception('Token validation failed: %s', e)
            return jsonify({'error': 'Forbidden', 'detail': 'Invalid or expired token'}), 403
        g.current_user = claims.get('cognito:username') or claims.get('sub')
        _provision_user(g.current_user)
        return f(*args, **kwargs)
    return wrapper
