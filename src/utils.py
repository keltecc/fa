#!/usr/bin/env python3

import hashlib

import jwt


JWT_ALGORITHM = 'HS256'


def hash_password(password: str) -> str:
    salt = b'bebrik'
    pepper = b'kekosik'

    result = hashlib.sha256(salt + password.encode() + pepper)
    
    return result.hexdigest()


def create_jwt_token(secret: str, obj: dict) -> str:
    return jwt.encode(obj, secret, algorithm = JWT_ALGORITHM)


def validate_jwt_token(secret: str, token: str) -> dict:
    return jwt.decode(token, secret, algorithms = [JWT_ALGORITHM])
