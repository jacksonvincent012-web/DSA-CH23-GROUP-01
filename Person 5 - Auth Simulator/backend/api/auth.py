"""
PHASE 3 — JWT Authentication & RBAC
Rubric requirement: Auth layer for multi-tenant access control

WHY JWT + RBAC?
  Stateless tokens allow horizontal scaling (no server-side session store).
  Three roles (viewer / analyst / admin) map directly to the API permission
  matrix defined in Step 3 of the system design.
"""

import os
import time
import hashlib
import secrets
from functools import wraps

import jwt
from flask import request, jsonify, g

# ------------------------------------------------------------------ #
# Configuration                                                       #
# ------------------------------------------------------------------ #

SECRET_KEY = os.environ.get("JWT_SECRET", "dsa-ch23-stock-query-secret-dev")
ACCESS_EXPIRY = 3600          # 1 hour
REFRESH_EXPIRY = 7 * 86400    # 7 days

# ------------------------------------------------------------------ #
# In-memory user store (Phase 1 — replaced by DB in Phase 2)          #
# ------------------------------------------------------------------ #

_users: dict[str, dict] = {}   # email -> { password_hash, role, refresh_tokens, ... }

# Seed demo accounts
def _hash_pw(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def _seed_users():
    users = [
        ("admin@stockquery.io",   "admin123",   "admin"),
        ("analyst@stockquery.io", "analyst123", "analyst"),
        ("viewer@stockquery.io",  "viewer123",  "viewer"),
    ]
    for email, pw, role in users:
        _users[email] = {
            "email": email,
            "password_hash": _hash_pw(pw),
            "role": role,
            "refresh_tokens": [],
        }
_seed_users()

# ------------------------------------------------------------------ #
# JWT helpers                                                         #
# ------------------------------------------------------------------ #

def _make_token(email: str, role: str, expiry: int) -> str:
    payload = {
        "email": email,
        "role": role,
        "exp": int(time.time()) + expiry,
        "iat": int(time.time()),
        "jti": secrets.token_hex(8),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def _decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

# ------------------------------------------------------------------ #
# Flask decorators                                                    #
# ------------------------------------------------------------------ #

def require_auth(f):
    """Require a valid JWT access token. Sets g.user on success."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401
        token = auth_header[7:]
        payload = _decode_token(token)
        if payload is None:
            return jsonify({"error": "Invalid or expired token"}), 401
        g.user = payload
        return f(*args, **kwargs)
    return wrapper

def require_role(*roles: str):
    """Restrict access to specific roles. Must follow @require_auth."""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if g.user.get("role") not in roles:
                return jsonify({"error": "Insufficient permissions"}), 403
            return f(*args, **kwargs)
        return wrapper
    return decorator

def optional_auth(f):
    """Try to decode JWT but do not require it. Sets g.user or None."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        g.user = None
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            payload = _decode_token(auth_header[7:])
            if payload:
                g.user = payload
        return f(*args, **kwargs)
    return wrapper

# ------------------------------------------------------------------ #
# Route handlers — called by server.py                                #
# ------------------------------------------------------------------ #

def handle_register(data: dict) -> tuple:
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    role = data.get("role", "viewer")

    if not email or not password:
        return {"error": "Email and password required"}, 400
    if role not in ("viewer", "analyst", "admin"):
        return {"error": "Invalid role — must be viewer, analyst, or admin"}, 400
    if email in _users:
        return {"error": "Email already registered"}, 409

    _users[email] = {
        "email": email,
        "password_hash": _hash_pw(password),
        "role": role,
        "refresh_tokens": [],
    }
    return {"message": "User registered", "email": email, "role": role}, 201


def handle_login(data: dict) -> tuple:
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    user = _users.get(email)
    if not user or user["password_hash"] != _hash_pw(password):
        return {"error": "Invalid email or password"}, 401

    access_token = _make_token(email, user["role"], ACCESS_EXPIRY)
    refresh_token = _make_token(email, user["role"], REFRESH_EXPIRY)
    user["refresh_tokens"].append(refresh_token)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "email": email,
        "role": user["role"],
    }, 200


def handle_refresh(data: dict) -> tuple:
    refresh_token = data.get("refresh_token", "")

    # Find user who owns this refresh token
    for email, user in _users.items():
        if refresh_token in user["refresh_tokens"]:
            payload = _decode_token(refresh_token)
            if payload is None:
                return {"error": "Refresh token expired"}, 401
            # Issue new access token
            access_token = _make_token(email, user["role"], ACCESS_EXPIRY)
            return {"access_token": access_token}, 200

    return {"error": "Invalid refresh token"}, 401


def handle_me() -> dict:
    if not g.user:
        return {"error": "Not authenticated"}, 401
    return {
        "email": g.user["email"],
        "role": g.user["role"],
    }, 200


def handle_logout(data: dict) -> tuple:
    refresh_token = data.get("refresh_token", "")
    for user in _users.values():
        if refresh_token in user["refresh_tokens"]:
            user["refresh_tokens"].remove(refresh_token)
            return {"message": "Logged out"}, 200
    return {"error": "Invalid refresh token"}, 401


def get_user_count() -> int:
    return len(_users)
