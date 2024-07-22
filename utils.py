from typing import Dict, Optional
from fastapi import HTTPException, Header
from jose import JWTError, jwt
import logging
import os
from dotenv import load_dotenv
from pydantic import ValidationError

from schemas import JWTPayload

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
API_KEY = os.getenv("API_KEY")
SUPPORTED_ALGORITHMS = list(os.getenv("SUPPORTED_ALGORITHMS", "").split(','))

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def verify_token(token: str) -> JWTPayload:
    credentials_exception = HTTPException(
        status_code=403, detail="Could not validate credentials"
    )
    required_fields = {"sub", "name", "iat", "exp", "context-role"}

    try:
        # Decode the JWT header
        header = jwt.get_unverified_header(token)
        logging.debug(f"JWT header: {header}")

        # Decode the JWT payload#
        payload = jwt.decode(token, SECRET_KEY, algorithms=SUPPORTED_ALGORITHMS)
        logging.debug(f"Decoded payload: {payload}")

        # Validate required fields
        try:
            payload = JWTPayload(**payload)
        except ValidationError as e:
            logging.error(e.errors())
            raise credentials_exception

        # Ensure the token is extremely short-lived
        if payload.exp - payload.iat > 30:
            logging.error(f"Token validation failed: Token expiry exceeds limit")
            raise credentials_exception

        logging.debug(f"Token validation successful for user: {payload.sub}")
        return payload
    except JWTError as e:
        logging.error(f"JWT validation error: {e}")
        raise credentials_exception


def verify_api_key(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=403, detail="Missing API Key")
    if authorization != f'Bearer {API_KEY}':
        raise HTTPException(status_code=403, detail="Invalid API Key")
