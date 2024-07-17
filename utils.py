from fastapi import HTTPException, Header

API_KEY = "mysecureapikey"


def verify_api_key(authorization: str = Header(...)):
    if authorization != f"Bearer {API_KEY}":
        raise HTTPException(status_code=403, detail="Invalid API Key")
