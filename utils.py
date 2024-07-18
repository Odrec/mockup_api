from typing import Dict, Optional
from fastapi import HTTPException, Header
from jose import JWTError, jwt
import logging
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
API_KEY = os.getenv("API_KEY")

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def verify_token(token: str) -> Dict:
    credentials_exception = HTTPException(
        status_code=403, detail="Could not validate credentials"
    )
    required_fields = {"sub", "name", "iat", "exp", "context-role"}

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logging.debug(f"Decoded payload: {payload}")

        # Check the presence of required fields
        if not required_fields.issubset(payload.keys()):
            logging.error(f"Token validation failed: Missing required fields")
            raise credentials_exception

        # Validate specific fields
        if not isinstance(payload.get("sub"), str):
            logging.error(f"Token validation failed: 'sub' is not a string")
            raise credentials_exception

        if not isinstance(payload.get("name"), str):
            logging.error(f"Token validation failed: 'name' is not a string")
            raise credentials_exception

        if not isinstance(payload.get("iat"), int):
            logging.error(f"Token validation failed: 'iat' is not an integer")
            raise credentials_exception

        if not isinstance(payload.get("exp"), int):
            logging.error(f"Token validation failed: 'exp' is not an integer")
            raise credentials_exception

        if "context" in payload and not isinstance(payload.get("context"), str):
            logging.error(f"Token validation failed: 'context' is not a string")
            raise credentials_exception

        if not isinstance(payload.get("context-role"), str):
            logging.error(f"Token validation failed: 'context-role' is not a string")
            raise credentials_exception

        # Ensure the token is extremely short-lived
        if payload.get("exp") - payload.get("iat") > 30:
            logging.error(f"Token validation failed: Token expiry exceeds limit")
            raise credentials_exception

        logging.debug(f"Token validation successful for user: {payload.get('sub')}")
        return payload
    except JWTError as e:
        logging.error(f"JWT validation error: {e}")
        raise credentials_exception


def verify_api_key(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=403, detail="Missing API Key")
    if authorization != f'Bearer {API_KEY}':
        raise HTTPException(status_code=403, detail="Invalid API Key")
